import typing

import tortoise
import tortoise.transactions
from tortoise.transactions import atomic
from fastapi_pagination.ext.tortoise import paginate
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.expressions import F, Q, RawSQL
from tortoise.functions import Concat

from api import enums, security, exceptions
from .. import models
from .. import schemas
from .. import utils
from ..conf import conf
from . import fields as custom_fields
from . import mixins
from ..exceptions import HTTPBadRequestException
from ..services import sms
from ..services.sms.notification import send_confirm_email_otp


fields = tortoise.fields


class UserAlreadyExists(Exception):
    """Raises if user with given credentials already exists."""


class UserNotFound(Exception):
    """Raises if user with provided ID not found."""


class User(mixins.DeleteFilesMixin, tortoise.models.Model):
    id = fields.IntField(pk=True)
    phone_number = fields.CharField(max_length=13, unique=True)
    email = fields.CharField(unique=True, null=True, max_length=50)
    password = fields.CharField(max_length=500, null=True)
    first_name = fields.CharField(max_length=32, null=True, index=True)
    last_name = fields.CharField(max_length=32, null=True, index=True)
    middle_name = fields.CharField(max_length=32, null=True, index=True)
    iin = fields.CharField(max_length=12, unique=True, null=True, index=True)
    photo = custom_fields.ImageField(upload_to='users/photos', null=True)
    personal_agreement = custom_fields.FileField(
        upload_to='users/personal-agreements',
        null=True)
    credentials = fields.JSONField(null=True)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    permissions: fields.ManyToManyRelation[
        'models.Permission'] = fields.ManyToManyField(
        'versions.Permission',
        related_name='users',
    )

    # type hints
    profile_courier: fields.ReverseRelation['models.ProfileCourier']
    profile_dispatcher: fields.ReverseRelation['models.ProfileDispatcher']
    profile_manager: fields.ReverseRelation['models.ProfileManager']
    profile_owner: fields.ReverseRelation['models.ProfileOwner']
    profile_service_manager: fields.ReverseRelation[
        'models.ProfileServiceManager']
    profile_branch_manager: fields.ReverseRelation[
        'models.ProfileBranchManager']
    fcmdevices: fields.ReverseRelation['models.FCMDevice']

    class Meta:
        table = 'user'
        ordering = ('-created_at',)

    @property
    def fullname(self):
        return f'{self.last_name or ""} {self.first_name or ""} {self.middle_name or ""}'.strip()

    @property
    def pwd_context(self):
        return CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def check_password(self, password, hashed_password: str = None) -> bool:
        if hashed_password is None:
            hashed_password = self.password
        return self.pwd_context.verify(password, hashed_password)

    def set_password(self, password):
        self.password = self.hash_password(password)

    @classmethod
    async def authenticate(cls, username: str, password):
        if len(username) > cls._meta.fields_map['phone_number'].max_length:
            user = await cls.filter(email=username).first()
        else:
            user = await cls.filter(Q(phone_number=username) | Q(email=username)).first()
        if not user:
            return
        return user if user.check_password(password) else None


async def user_get_object_or_404(user_id: int, **kwargs):
    try:
        return await User.get(id=user_id, **kwargs)
    except DoesNotExist:
        raise DoesNotExist(
            f'User with provided ID: {user_id} not found',
        )


async def user_get(**kwargs) -> dict:
    with_history = kwargs.pop('with_history', True)
    try:
        user = await User.annotate(has_password=RawSQL('"password" IS NOT NULL')).get(**kwargs).values()
        user.pop('password', None)
    except tortoise.exceptions.DoesNotExist as e:
        values = ', '.join([str(item) for item in kwargs.values()])
        raise UserNotFound(
            f'User with provided {", ".join(kwargs.keys())}: {values} not '
            f'found',
        ) from e

    if with_history:
        try:
            user['invited_by'] = await models.invited_user_get(
                phone_number=user['phone_number'])
        except models.InvitedUserNotFound:
            user['invited_by'] = None
    return user


async def user_get_multiple_profiles(**kwargs) -> dict:
    with_history = kwargs.pop('with_history', True)
    try:
        user = await User.annotate(has_password=RawSQL('"password" IS NOT NULL')).get(**kwargs).values()
        user.pop('password', None)
    except tortoise.exceptions.DoesNotExist as e:
        values = ', '.join([str(item) for item in kwargs.values()])
        raise UserNotFound(
            f'User with provided {", ".join(kwargs.keys())}: {values} not '
            f'found',
        ) from e
    try:
        profiles = await models.profile_get_multiple(user['id'])
        for profile in profiles:

            partner_id = profile['profile_content'].get('partner_id')
            user['partners'] = [partner_id]

            if partner_id:
                if profile['profile_type'] == enums.ProfileType.DISPATCHER:
                    user['partners'].extend(
                        await models.Partner.filter(
                            dispatcher_set=profile['id'],
                        ).values_list('id', flat=True)
                    )
                else:
                    user['partners'].extend(await models.Partner.filter(
                        courier_partner_id=partner_id).values_list('id', flat=True))
                if profile['profile_type'] == enums.ProfileType.COURIER:
                    areas = await models.Area.filter(
                        couriers=profile.get('id')
                    )
                    area_list = []
                    for area in areas:
                        area_obj = {'id': area.id, 'name': area.slug}
                        area_list.append(area_obj)
                    profile['profile_content']['areas'] = area_list
        user['profiles'] = profiles
    except (
        models.ProfileNotFound,
        models.InvitedUserNotFound,
    ):

        pass
    if with_history:
        try:
            user['invited_by'] = await models.invited_user_get(
                phone_number=user['phone_number'])
        except models.InvitedUserNotFound:
            user['invited_by'] = None
    return user


async def get_user_profile_with_info(profile_type, profile_id, user=None):
    if user is None:
        user = {}
    try:
        profile = await models.profile_get_by_profile_type(
            profile_type=profile_type, profile_id=profile_id)
        if not isinstance(profile, dict):
            profile = profile.dict()

        user['profile'] = profile
        partner_id = profile['profile_content'].get('partner_id')
        user['partners'] = [partner_id]
        if partner_id:
            match user['profile']['profile_type']:
                case enums.ProfileType.BRANCH_MANAGER:
                    user['partners'].extend(
                        await models.Partner.filter(
                            courier_partner_id=partner_id,
                        ).values_list('id', flat=True),
                    )
                case enums.ProfileType.DISPATCHER:
                    user['partners'].extend(
                        await models.Partner.filter(
                            dispatcher_set=user['profile']['id'],
                        ).values_list('id', flat=True)
                    )

                case enums.ProfileType.COURIER:
                    user['partners'].extend(await models.Partner.filter(
                        courier_partner_id=partner_id).values_list('id', flat=True))
                    areas = await models.Area.filter(
                        couriers=user['profile']['id'],
                    )
                    area_list = []
                    for area in areas:
                        area_obj = {'id': area.id, 'name': area.slug}
                        area_list.append(area_obj)
                    user['profile']['profile_content']['areas'] = area_list
                case enums.ProfileType.SERVICE_MANAGER:
                    user['partners'].extend(await models.Partner.filter(
                        courier_partner_id=partner_id).values_list('id', flat=True))
                case enums.ProfileType.SUPERVISOR:
                    user['partners'].extend(await models.Partner.filter(
                        courier_partner_id=partner_id).values_list('id', flat=True))
                case enums.ProfileType.LOGIST:
                    user['partners'].extend(await models.Partner.filter(
                        courier_partner_id=partner_id).values_list('id', flat=True))
                case enums.ProfileType.CALL_CENTER_MANAGER:
                    user['partners'].extend(await models.Partner.filter(
                        courier_partner_id=partner_id).values_list('id', flat=True))
                case enums.ProfileType.GENERAL_CALL_CENTER_MANAGER:
                    user['partners'].extend(await models.Partner.filter(
                        courier_partner_id=partner_id).values_list('id', flat=True))
                case enums.ProfileType.SUPPORT:
                    user['partners'].extend(await models.Partner.filter(
                        courier_partner_id=partner_id).values_list('id', flat=True))
        return user
    except (
        models.ProfileNotFound,
        models.InvitedUserNotFound,
    ):

        pass


async def user_get_by_phone_number(phone_number: str) -> User:
    if len(phone_number) > User._meta.fields_map['phone_number'].max_length:
        raise UserNotFound(
            f'User with provided credentials: {phone_number} not found',
        )

    try:
        user = await User.get(phone_number=phone_number)
        return user
    except tortoise.exceptions.DoesNotExist as e:
        raise UserNotFound(
            f'User with provided phone number: {phone_number} not found',
        ) from e


async def user_get_by_email(email: str) -> User:
    try:
        user = await User.get(email=email)
        return user
    except tortoise.exceptions.DoesNotExist as e:
        raise UserNotFound(
            f'User with provided email: {email} not found',
        ) from e


async def user_get_list(pagination_params, **kwargs):
    search_type = kwargs.pop('search_type')
    search = kwargs.pop('search')
    profile_type = kwargs.pop('profile_type')
    area_id = kwargs.pop('area_id', None)
    partner_id__in = kwargs.pop('partner_id__in')
    invite_status = kwargs.pop('invite_status', None)
    if profile_type is not None:
        profile_type_kwarg = profile_type
        table_name = models.profile_types_to_models[
            profile_type_kwarg].Meta.table

        if profile_type_kwarg == enums.ProfileType.COURIER and area_id:
            kwargs[
                f'{table_name}__areas__id'
            ] = area_id
        kwargs[f'{table_name}__partner_id__in'] = partner_id__in

        profile_type_kwarg = {
            f'{table_name}__isnull': False}
        kwargs.update(profile_type_kwarg)
    queryset = User.filter(**kwargs)
    if search and search_type:
        if search_type == enums.UserSearchType.FULL_NAME:
            queryset = queryset.annotate(
                full_name=(Concat('first_name', ' ', F('middle_name'), ' ', F('last_name')))
            ).filter(full_name__icontains=search)
        elif search_type == enums.UserSearchType.IIN:
            queryset = queryset.filter(iin__icontains=search)
        elif search_type == enums.UserSearchType.PHONE:
            queryset = queryset.filter(phone_number__icontains=search)
    if profile_type == enums.ProfileType.COURIER:
        if invite_status:
           queryset = queryset.filter(profile_courier__status=invite_status)
        paginated_result = await paginate(queryset, pagination_params)
        for user in paginated_result.items:
            try:
                user.invited_by = await models.invited_user_get(phone_number=user.phone_number)
            except models.InvitedUserNotFound:
                user.invited_by = None
            user_with_multiple_profiles = await models.user_get_multiple_profiles(id=user.id,
                                                                                  with_history=True)
            user.profiles = user_with_multiple_profiles.get('profiles')
            for profile in user.profiles:
                if profile.get('profile_type') == enums.ProfileType.COURIER:
                    user.last_message = await models.ExternalServiceHistory.filter(
                        service_name=enums.ExternalServices.SMS.value,
                        request_body__contains={'mobile_phone': str(user.phone_number)}
                    ).annotate(request_body_str=F('request_body')).filter(
                        request_body_str__icontains='приглашает вас зарегистрироваться'
                    ).first().values('request_body', 'created_at')

                    areas = await models.Area.filter(
                        couriers=profile['id'],
                    )
                    area_list = []
                    for area in areas:
                        area_obj = {'id': area.id, 'name': area.slug}
                        area_list.append(area_obj)
                    profile['profile_content']['areas'] = area_list
        return paginated_result

    ids = await queryset.values_list('id', flat=True)
    users = [await user_get_multiple_profiles(id=id_) for id_ in ids]
    return users


async def user_change_photo(user_id, photo):
    try:
        user = await User.get(id=user_id)
        user.photo = photo
        await user.save()
        await user.refresh_from_db()
        return {'photo': user.photo}
    except tortoise.exceptions.DoesNotExist as e:
        raise UserNotFound(
            f'User with provided ID: {user_id} not found',
        ) from e


async def user_create(
    user: typing.Union[schemas.UserCreate, schemas.UserCreateManually],
    **kwargs,
) -> dict:
    try:
        created = await User.create(**user.dict(exclude_unset=True))
    except IntegrityError:
        raise exceptions.HTTPBadRequestException('This user exists')
    current_user = kwargs.pop('current_user', None)
    if kwargs.get('inviter_id') and current_user is not None:
        await models.invited_user_create(
            schema=schemas.InvitedUserCreate(
                phone_number=created.phone_number,
                profile_type=current_user.profile['profile_type']
            ),
            **kwargs,
        )
    user = await models.user_get(id=created.id)
    return user


async def user_update(user_id: int, update: schemas.UserUpdate) -> dict:
    try:
        user = await User.get(id=user_id)
    except tortoise.exceptions.DoesNotExist as e:
        raise UserNotFound(
            f'User with provided ID: {user_id} not found',
        ) from e
    try:
        await user.update_from_dict(update.dict(exclude_unset=True)).save()
    except tortoise.exceptions.IntegrityError as e:
        for arg in e.args:
            if 'phone_number' in arg.detail:
                raise UserAlreadyExists(
                    f'User with given phone number: '
                    f'{update.phone_number} already exists',
                )
            if 'iin' in arg.detail:
                raise UserAlreadyExists(
                    f'User with given iin: {update.iin} already exists',
                )

    return await user_get(id=user_id)


async def user_delete(user_id: int) -> None:
    try:
        user = await User.get(id=user_id)
    except tortoise.exceptions.DoesNotExist as e:
        raise UserNotFound(
            f'User with provided ID: {user_id} not found',
        ) from e

    await user.delete()


async def user_permission_add(user_id: int, permission_slug: str):
    instance = await user_get_object_or_404(user_id=user_id)
    permission = await models.permission_get_or_404(
        permission_slug=permission_slug)

    await instance.permissions.add(permission)

    user = utils.as_dict(record=instance)
    user['permissions'] = await models.Permission.filter(users=user_id).values(
        'id',
        'name')

    return user


async def user_permission_remove(user_id: int, permission_slug: str):
    instance = await user_get_object_or_404(user_id=user_id)
    permission = await models.permission_get_or_404(
        permission_slug=permission_slug)

    await instance.permissions.remove(permission)

    user = utils.as_dict(record=instance)
    user['permissions'] = await models.Permission.filter(
        users=user_id,
    ).values('id', 'name')

    return user


@atomic()
async def user_set_password(user_id, email, password, token):
    user_obj = await User.get(id=user_id)
    if email is not None:
        if await models.User.filter(id__not=user_obj.id, email=email).exists():
            raise HTTPBadRequestException('this email belongs to another user')
    if email and user_obj.email != email:
        if not conf.api.debug and email == 'jedelloggy@rambler.ru':
            otp_code = 8542
        else:
            otp_code = await models.utils.create_otp()
        if conf.api.debug:
            await sms.otp_service.send_email_verification_otp(
                email=email, user_id=user_id, otp_code=otp_code
            )
        else:
            await send_confirm_email_otp(email, otp_code=otp_code, user_id=user_id)
    user_obj.set_password(password)

    # means this token generated for magic link and should be revoked
    if 'email' in security.unsign_token(token):
        await models.token_revoke(token)
    await user_obj.save()


@atomic()
async def user_set_password_v2(user_id, password, token):
    user_obj = await User.get(id=user_id)
    user_obj.set_password(password)

    # means this token generated for magic link
    if 'email' in security.unsign_token(token).get('email'):
        await models.token_revoke(token)
    await user_obj.save()
