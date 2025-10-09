import datetime
import typing
from zoneinfo import ZoneInfo

import dateutil.relativedelta as delta
from pydantic import parse_obj_as
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.exceptions import IntegrityError
from tortoise.models import MODEL
from tortoise.models import Model
from tortoise.models import Q
from tortoise.timezone import now
from tortoise.transactions import atomic
from api.modules.shipment_point.schemas import CityGet
from dateutil import rrule

from api.conf import conf
from . import fields as custom_fields
from .. import enums, security, redis_module
from .. import models
from .. import schemas
from .. import times
from .. import utils
from ..modules.city.infrastructure.db_table import City
from ..modules.shipment_point import PartnerShipmentPoint
from ..services.sms.notification import send_email_magic_link


class ProfileAlreadyExists(Exception):
    """Raises if profile with provided ID already exists."""


class ProfileNotFound(DoesNotExist):
    """Raises if profile with provided ID not found."""


class StatusAlreadySet(Exception):
    """Raises if courier status already changed"""


class ProfileOwner(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        'versions.User',
        'profile_owner',
    )
    partner: fields.OneToOneRelation['models.Partner'] = fields.OneToOneField(
        'versions.Partner',
        'leader',
    )

    # type hints
    partner_id: int
    user_id: int

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'profile_owner'


class ProfileCourier(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        'versions.User',
        'profile_courier',
    )
    partner: fields.ForeignKeyRelation[
        'models.Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        'couriers',
    )
    city: fields.ForeignKeyRelation['City'] = fields.ForeignKeyField(
        'versions.City',
        'couriers',
        fields.SET_NULL,
        null=True,
    )
    category: fields.ForeignKeyNullableRelation[
        'models.Category'
    ] = fields.ForeignKeyField(
        'versions.Category',
        'couriers',
        fields.SET_NULL,
        null=True,
    )
    at_work = fields.BooleanField(default=False)
    experience_years = fields.IntField(null=True)
    experience_months = fields.IntField(null=True)
    start_work_hour = fields.CharField(min_length=5, max_length=5, null=True)
    end_work_hour = fields.CharField(min_length=5, max_length=5, null=True)
    schedule = custom_fields.CharArrayField(max_length=7, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_identified = fields.BooleanField(default=False)
    is_biometry_verificated = fields.BooleanField(default=False)
    register_with_biometry = fields.BooleanField(default=False)
    iban = fields.CharField(max_length=34, min_length=16,
                            null=True)  # nullable only for success migration
    item_type = fields.CharEnumField(**enums.ItemType.to_kwargs(null=True))
    transport_type = fields.CharEnumField(
        **enums.TransportType.to_kwargs(null=True))
    state = fields.CharEnumField(**enums.CourierState.to_kwargs(null=True))
    status = fields.CharEnumField(
        **enums.InviteStatus.to_kwargs(default=enums.InviteStatus.INVITED))
    areas: fields.ManyToManyRelation['models.Area'] = fields.ManyToManyField(
        'versions.Area',
        related_name='couriers',
    )

    # type hints
    user_id: int
    partner_id: int
    ratings: fields.ReverseRelation['models.Rate']
    city_id: int
    category_id: int
    area_id: int

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'profile_courier'

    @property
    async def current_rate(self):
        filter_kwargs = {
            'courier_id': self.id,
            'created_at': now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        }
        rate = await models.Rate.filter(**filter_kwargs).first()
        if not rate:
            rate = await models.Rate.create(**filter_kwargs)
        return rate

    @property
    async def city_tz(self) -> ZoneInfo:
        if not isinstance(self.city, City):
            await self.fetch_related('city')
        if self.city is None:
            return ZoneInfo('UTC')
        return self.city.tz

    @property
    async def localtime(self) -> datetime.datetime:
        current_time = now()
        city_tz = await self.city_tz
        return current_time + city_tz.utcoffset(current_time)


class ProfileDispatcher(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        'versions.User',
        related_name='profile_dispatcher',
    )
    partner: fields.ForeignKeyRelation[
        'models.Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        related_name='dispatchers',
    )
    partners: fields.ManyToManyRelation['models.Partner'] = fields.ManyToManyField(
        'versions.Partner',
        related_name='dispatcher_set',
    )

    # type hints
    user_id: int
    partner_id: int

    class Meta:
        table = 'profile_dispatcher'


class ProfileManager(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        'versions.User',
        related_name='profile_manager',
    )
    partner: fields.ForeignKeyRelation[
        'models.Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        related_name='managers',
    )

    # type hints
    user_id: int
    partner_id: int

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'profile_manager'


class ProfileBankManager(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        'versions.User',
        related_name='profile_bank_manager',
    )
    partner: fields.ForeignKeyRelation[
        'models.Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        to_field='id',
        related_name='bank_managers',
    )

    # type hints
    user_id: int
    partner_id: int

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'profile_bank_manager'


class ProfileServiceManager(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        'versions.User',
        'profile_service_manager',
    )
    partner: fields.ForeignKeyRelation[
        'models.Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        related_name='service_managers',
    )

    # type hints
    partner_id: int
    user_id: int

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'profile_service_manager'


class ProfileBranchManager(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        'versions.User',
        'profile_branch_manager',
    )
    partner: fields.ForeignKeyRelation[
        'models.Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        'branch_managers',
    )
    cities: fields.ManyToManyRelation['City'] = fields.ManyToManyField(
        'versions.City',
        related_name='city_set',
    )
    # type hints
    partner_id: int
    user_id: int

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'profile_branch_manager'


class ProfilePartnerBranchManager(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        'versions.User',
        'profile_partner_branch_manager',
    )
    partner: fields.ForeignKeyRelation[
        'models.Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        'partner_branch_managers',
    )
    shipment_point: fields.ForeignKeyRelation[
        'PartnerShipmentPoint'] = fields.ForeignKeyField(
        'versions.PartnerShipmentPoint',
        'partner_branch_manager',
    )
    # type hints
    partner_id: int
    user_id: int
    shipment_point_id: int

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'profile_partner_branch_manager'


class ProfileSorter(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField('versions.User',
                                                                        'profile_sorter')
    partner: fields.ForeignKeyRelation['models.Partner'] = fields.ForeignKeyField(
        'versions.Partner', 'sorters')
    shipment_point: fields.ForeignKeyRelation[
        'PartnerShipmentPoint'] = fields.ForeignKeyField(
        'versions.PartnerShipmentPoint',
        'sorters',
    )

    # type hints
    user_id: int
    partner_id: int
    shipment_point_id: int

    class Meta:
        table = 'profile_sorter'


class ProfileSupervisor(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        model_name='versions.User',
        on_delete=fields.CASCADE,
        related_name='profile_supervisor',
    )
    partner: fields.ForeignKeyRelation['models.Partner'] = fields.ForeignKeyField(
        model_name='versions.Partner',
        on_delete=fields.CASCADE,
        related_name='profile_supervisor',
    )
    country: fields.ForeignKeyRelation['models.Country'] = fields.ForeignKeyField(
        model_name='versions.Country',
        on_delete=fields.CASCADE,
        related_name='profile_supervisor',
    )

    class Meta:
        table = 'profile_supervisor'


class ProfileLogist(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        model_name='versions.User',
        on_delete=fields.CASCADE,
        related_name='profile_logist',
    )
    partner: fields.ForeignKeyRelation['models.Partner'] = fields.ForeignKeyField(
        model_name='versions.Partner',
        on_delete=fields.CASCADE,
        related_name='profile_logist',
    )
    country: fields.ForeignKeyRelation['models.Country'] = fields.ForeignKeyField(
        model_name='versions.Country',
        on_delete=fields.CASCADE,
        related_name='profile_logist',
    )

    class Meta:
        table = 'profile_logist'


class ProfileCallCenterManager(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        model_name='versions.User',
        on_delete=fields.CASCADE,
        related_name='profile_call_center_manager',
    )
    partner: fields.ForeignKeyRelation['models.Partner'] = fields.ForeignKeyField(
        model_name='versions.Partner',
        on_delete=fields.CASCADE,
        related_name='profile_call_center_manager',
    )
    country: fields.ForeignKeyRelation['models.Country'] = fields.ForeignKeyField(
        model_name='versions.Country',
        on_delete=fields.CASCADE,
        related_name='profile_call_center_manager',
    )

    class Meta:
        table = 'profile_call_center_manager'


class ProfileGeneralCallCenterManager(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        model_name='versions.User',
        on_delete=fields.CASCADE,
        related_name='profile_general_call_center_manager',
    )
    partner: fields.ForeignKeyRelation['models.Partner'] = fields.ForeignKeyField(
        model_name='versions.Partner',
        on_delete=fields.CASCADE,
        related_name='profile_general_call_center_manager',
    )

    class Meta:
        table = 'profile_general_call_center_manager'


class ProfileSupport(Model):
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation['models.User'] = fields.OneToOneField(
        model_name='versions.User',
        on_delete=fields.CASCADE,
        related_name='profile_support',
    )
    partner: fields.ForeignKeyRelation['models.Partner'] = fields.ForeignKeyField(
        model_name='versions.Partner',
        on_delete=fields.CASCADE,
        related_name='profile_support',
    )

    class Meta:
        table = 'profile_support'



profile_types_to_models = {
    enums.ProfileType.BRANCH_MANAGER: ProfileBranchManager,
    enums.ProfileType.COURIER: ProfileCourier,
    enums.ProfileType.DISPATCHER: ProfileDispatcher,
    enums.ProfileType.MANAGER: ProfileManager,
    enums.ProfileType.OWNER: ProfileOwner,
    enums.ProfileType.PARTNER_BRANCH_MANAGER: ProfilePartnerBranchManager,
    enums.ProfileType.SERVICE_MANAGER: ProfileServiceManager,
    enums.ProfileType.SORTER: ProfileSorter,
    enums.ProfileType.BANK_MANAGER: ProfileBankManager,
    enums.ProfileType.SUPERVISOR: ProfileSupervisor,
    enums.ProfileType.LOGIST: ProfileLogist,
    enums.ProfileType.CALL_CENTER_MANAGER: ProfileCallCenterManager,
    enums.ProfileType.GENERAL_CALL_CENTER_MANAGER: ProfileGeneralCallCenterManager,
    enums.ProfileType.SUPPORT: ProfileSupport,
}

profile_to_schemas = {
    enums.ProfileType.BRANCH_MANAGER: schemas.ProfileBranchManagerCreate,
    enums.ProfileType.COURIER: schemas.ProfileCourierCreate,
    enums.ProfileType.DISPATCHER: schemas.ProfileDispatcherCreate,
    enums.ProfileType.MANAGER: schemas.ProfileManagerCreate,
    enums.ProfileType.OWNER: schemas.ProfileOwnerCreate,
    enums.ProfileType.PARTNER_BRANCH_MANAGER: schemas.ProfileBranchManagerCreate,
    enums.ProfileType.SERVICE_MANAGER: schemas.ProfileServiceManagerCreate,
    enums.ProfileType.SORTER: schemas.ProfileSorterCreate,
    enums.ProfileType.BANK_MANAGER: schemas.ProfileBankManagerCreate,
    enums.ProfileType.SUPERVISOR: schemas.ProfileSupervisorCreate,
    enums.ProfileType.LOGIST: schemas.ProfileLogistCreate,
    enums.ProfileType.CALL_CENTER_MANAGER: schemas.ProfileCallCenterManagerCreate,
    enums.ProfileType.GENERAL_CALL_CENTER_MANAGER: schemas.ProfileGeneralCallCenterManagerCreate,
    enums.ProfileType.SUPPORT: schemas.ProfileSupportCreate,
}

OneOfProfiles = typing.Union[
    ProfileCourier,
    ProfileDispatcher,
    ProfileManager,
    ProfileOwner,
    ProfileServiceManager,
    ProfileBranchManager,
    ProfilePartnerBranchManager,
    ProfileSorter,
    ProfileBankManager,
    ProfileSupervisor,
    ProfileLogist,
    ProfileCallCenterManager,
    ProfileGeneralCallCenterManager,
    ProfileSupport,
]


def _recalculate_courier_experience(profile: dict) -> tuple:
    created_at = profile['created_at']
    years = profile['experience_years']
    months = profile['experience_months']

    years = years if years is not None else 0
    months = months if months is not None else 0

    exp_before = (years * 12) + months
    exp_on_create = delta.relativedelta(dt1=created_at, months=exp_before)
    exp_current = delta.relativedelta(dt1=times.utcnow(), dt2=created_at)
    exp_total = exp_current + exp_on_create

    profile['experience_years'] = exp_total.years
    profile['experience_months'] = exp_total.months


async def get_all_user_profiles(user_id: int):
    profiles = []
    for key, model in profile_types_to_models.items():
        if profile := await model.filter(user_id=user_id).first():
            profiles.append({
                'type': key,
                'id': profile.id
            })
    return profiles


@utils.as_dict(from_model=True)
async def profile_get_list(
    pagination_params,
    profile_type: enums.ProfileType,
    **kwargs,
) -> list:
    result = []
    filter_kwargs = kwargs['filter_kwargs']
    filter_kwargs = filter(lambda item: item[1], filter_kwargs.items())
    profiles = await profile_types_to_models[profile_type].filter(**dict(filter_kwargs))
    for profile_obj in profiles:
        if profile_obj is not None:
            result.append(await profile_serialize(
                profile_obj, profile_type
            ))

    return result


async def profile_get_by_id(
    profile_id: int,
    profile_type: enums.ProfileType,
    **kwargs,
) -> MODEL:
    model = getattr(models, 'Profile' + profile_type.capitalize())
    try:
        return await model.get(id=profile_id, **kwargs)
    except DoesNotExist as e:
        raise ProfileNotFound(
            f'{profile_type} with given ID: {profile_id} was not found',
        )


async def profile_serialize(
    profile_obj: MODEL,
    profile_type: str,
    as_dict: bool = True,
    skip_dependency: bool = False,
):
    if profile_obj is not None:
        if as_dict:
            profile = utils.as_dict(record=profile_obj)
            if profile_type == enums.ProfileType.PARTNER_BRANCH_MANAGER:
                shipment_point = await PartnerShipmentPoint.get(
                    id=profile['shipment_point_id'],
                ).prefetch_related('partner')
                profile['shipment_point'] = schemas.ShipmentPointGet.from_orm(
                    shipment_point
                )

            if profile_type == enums.ProfileType.SORTER:
                shipment_point = await PartnerShipmentPoint.get(
                    id=profile['shipment_point_id'],
                ).prefetch_related('partner')
                partner = await models.Partner.get(id=profile_obj.partner_id)
                profile['shipment_point'] = schemas.ShipmentPointGet.from_orm(
                    shipment_point
                )
                profile['courier_partner_id'] = partner.courier_partner_id

            if profile_type == enums.ProfileType.BRANCH_MANAGER:
                profile['cities'] = parse_obj_as(
                    typing.List[CityGet],
                    await profile_obj.cities.all().select_related('country'),
                )

            if profile_type == enums.ProfileType.COURIER:
                profile['current_rate'] = (await profile_obj.current_rate).value
                category_obj = await profile_obj.category
                if category_obj:
                    profile['category'] = {
                        'name': category_obj.name,
                        'item_type': category_obj.item_type,
                        'value': category_obj.value,
                    }
                city = await profile_obj.city
                profile['city'] = {
                    'id': city.id,
                    'name': city.name,
                } if city else {
                    'id': None,
                    'name': None,
                }

                if not skip_dependency:
                    courier_id = profile['id']

                    _recalculate_courier_experience(profile)

                    delivered = await models.order_delivered_today(
                        courier_id)
                    deviation = await models.order_average_time_deviation(
                        courier_id)

                    profile['orders_delivered_today'] = delivered
                    profile['average_time_deviation'] = deviation
                    area_ids = await models.Area.filter(
                        couriers__id=profile.get('id')
                    ).values_list('id', flat=True)
                    profile['areas'] = area_ids
            if profile_type == enums.ProfileType.DISPATCHER:
                profile['partners'] = await profile_obj.partners.all().values(
                    'id', 'name_ru'
                )

            profile = {
                'id': profile.pop('id'),
                'user_id': profile.pop('user_id'),
                'profile_type': profile_type,
                'profile_content': profile,
            }

            return profile
        return profile_obj


async def profile_get_by_profile_type(profile_id: int, profile_type: str) -> MODEL:
    model = profile_types_to_models.get(profile_type)
    try:
        profile = await model.get(id=profile_id)
        return await profile_serialize(profile, profile_type, True, False)
    except DoesNotExist:
        raise ProfileNotFound(table='Profile', detail='Profile not found')


async def profile_get(
    as_dict: bool = True,
    skip_dependency: bool = False,
    **kwargs
) -> typing.Union[
    typing.Union[
        ProfileCourier,
        ProfileDispatcher,
        ProfileManager,
        ProfileOwner,
        ProfileServiceManager,
        ProfileBranchManager,
        ProfilePartnerBranchManager,
    ],
    dict,
]:
    for profile_type, model in profile_types_to_models.items():
        profile_obj = await model.filter(**kwargs).first()
        if profile_obj:
            return await profile_serialize(profile_obj, profile_type, as_dict, skip_dependency)

    raise ProfileNotFound(table='Profile', detail=f'Profile for provided user was not found')


async def profile_get_multiple(
    user_id: int,
    skip_dependency: bool = False,
) -> typing.List:
    profiles = []
    for profile_type, model in profile_types_to_models.items():
        profile_obj = None
        try:
            profile_obj = await model.get(user_id=user_id)
        except DoesNotExist:
            pass
        profile = await profile_serialize(profile_obj, profile_type, True, skip_dependency)
        if profile:
            profiles.append(profile)
    if profiles:
        return profiles

    raise ProfileNotFound(
        f'Profile for provided user ID: {user_id} was not found')


async def profile_biometry_verify(user_id: int,
                                  request_body: schemas.BiometryVerifyBody):
    for profile_type, model in profile_types_to_models.items():
        profile = await model.get_or_none(user_id=user_id)
        if request_body is not None and profile is not None:
            user = await models.User.get_or_none(id=profile.user_id)
            if user is not None:
                user.photo = request_body.user_photo
                await user.save(update_fields=['photo'])
        if profile is not None and profile_type == enums.ProfileType.COURIER:
            profile.is_biometry_verificated = bool(request_body.success)
            await profile.save(update_fields=['is_biometry_verificated'])
            return
    raise ProfileNotFound(
        f'Courier profile for provided user ID: {user_id} was not found')


async def profile_create(profile: schemas.ProfileCreate, model, user_id):
    content_dict = profile.profile_content.dict(exclude_unset=True)
    cities = content_dict.pop('cities', None)

    partners = content_dict.pop('partners', [])
    profile_created = await model.create(
        user_id=user_id,
        **content_dict,
    )
    if profile.profile_type == enums.ProfileType.DISPATCHER:
        partner_objects = await models.Partner.filter(id__in=partners)
        await profile_created.partners.add(*partner_objects)

    if profile.profile_type == enums.ProfileType.BRANCH_MANAGER:
        fetched_cities = await City.filter(id__in=cities)
        if fetched_cities:
            await profile_created.cities.add(*fetched_cities)

    group = await models.Group.filter(slug=profile.profile_type.value).first()
    if not group:
        group = await models.Group.create(slug=profile.profile_type.value)

    user = await models.User.get(id=user_id)

    await group.user_set.add(user)

    if profile.profile_type == enums.ProfileType.COURIER:
        await models.User.filter(id=user_id).update(is_active=False)

    as_dict = dict(profile_created)

    if profile.profile_type == enums.ProfileType.DISPATCHER:
        await profile_created.fetch_related('partners')
        as_dict['partners'] = await profile_created.partners.all().values(
            'id', 'name_ru',
        )

    return {
        'id': as_dict.pop('id'),
        'user_id': user_id,
        'profile_type': profile.profile_type,
        'profile_content': as_dict,
    }


@atomic()
async def create_profile_with_existing_user(profile: schemas.ProfileCreate, user):
    if user:
        model = profile_types_to_models[profile.profile_type]
        return await profile_create(profile=profile, model=model, user_id=user.id)
    raise models.UserNotFound(
        f'User with provided phone number {profile.user.phone_number} not found'
    )


@atomic()
async def create_profile_with_new_user(profile: schemas.ProfileCreate, **kwargs):
    user_created = await models.user_create(
        user=profile.user,
        **kwargs,
    )
    user_id = user_created['id']
    model = profile_types_to_models[profile.profile_type]
    profile_created = await profile_create(profile=profile, model=model, user_id=user_id)
    await profile_send_magic_link(kwargs.get('inviter_id'), profile.profile_type, profile_created['id'])
    return profile_created


@utils.save_in_history(
    request_method=enums.RequestMethods.POST,
    model_type='Profile',
)
async def new_profile_create(profile: schemas.ProfileCreate, **kwargs) -> dict:
    user = await models.User.filter(
        phone_number=profile.user.phone_number
    ).first()
    if user:
        return await create_profile_with_existing_user(profile=profile, user=user)
    return await create_profile_with_new_user(profile=profile, **kwargs)


async def profile_update(update, profile):
    update_data = update.profile_content.dict(exclude_unset=True)
    if (partners := update_data.pop('partners', None)) is not None:
        await profile.partners.clear()
        partner_objects = []
        for partner_id in partners:
            try:
                partner_objects.append(await models.Partner.get(id=partner_id))
            except DoesNotExist:
                raise models.PartnerNotFound(
                    f'Partner with given ID: {partner_id} was not found',
                )
        await profile.partners.add(*partner_objects)
    if update.profile_type == enums.ProfileType.BRANCH_MANAGER:
        if cities := update_data.pop('cities', None):
            await profile.cities.clear()
            fetched_cities = await City.filter(id__in=cities)
            if fetched_cities:
                await profile.cities.add(*fetched_cities)

    if update.profile_type == enums.ProfileType.COURIER:
        await profile.areas.clear()
        if (areas := update_data.pop('areas', None)) is not None:
            area_objects = []
            for area_id in areas:
                try:
                    area_objects.append(await models.Area.get(id=area_id))
                except DoesNotExist:
                    raise DoesNotExist(
                        f'Area with given ID: {area_id} was not found',
                    )
            await profile.areas.add(*area_objects)
    try:
        await profile.update_from_dict(update_data).save()
    except IntegrityError as e:
        for error in e.args:
            if 'partner_id' in error.detail:
                raise models.PartnerNotFound(
                    f'Partner with given ID: {update_data["partner_id"]} was '
                    f'not found',
                )

    redis_con = redis_module.get_connection()
    perm_cache_key = f"permissions:user_id:{profile.user_id}{'_profile:' + update.profile_type}"
    await redis_con.delete(perm_cache_key)

    return await profile_get_by_profile_type(profile_id=profile.id,
                                             profile_type=update.profile_type)


@utils.save_in_history(
    request_method=enums.RequestMethods.PUT,
    model_type='Profile',
)
@atomic()
async def profile_update_by_user_id(
    user_id: int,
    update: typing.Union[
        schemas.ProfileUpdate, schemas.ProfileUpdatePatch],
    is_patch: bool,
    partner__id__in,
) -> dict:
    model = profile_types_to_models[update.profile_type]

    try:
        profile = await model.get(user_id=user_id,
                                  partner__id__in=partner__id__in)
        return await profile_update(update, profile)
    except DoesNotExist as e:
        raise ProfileNotFound(
            f'Profile for provided user ID: {user_id} was not found',
        ) from e


@utils.save_in_history(
    request_method=enums.RequestMethods.PUT,
    model_type='Profile',
)
@atomic()
async def profile_update_by_profile_id(
    profile_id: int,
    update: typing.Union[
        schemas.ProfileUpdate, schemas.ProfileUpdatePatch]
) -> dict:
    model = profile_types_to_models[update.profile_type]

    try:
        profile = await model.get(id=profile_id)
        return await profile_update(update, profile)
    except DoesNotExist as e:
        raise ProfileNotFound(
            f'Profile with provided ID: {profile_id} was not found',
        ) from e


async def profile_status_update(
    user_id: int,
    update: typing.Union[
        schemas.ProfileStatusUpdate],
):
    try:
        status = update.status
        profile = await models.ProfileCourier.get(user_id=user_id)
        if status == enums.InviteStatus.REFUSED and profile.status != enums.InviteStatus.INVITED:
            raise StatusAlreadySet('Courier profile status already changed')
        profile.status = status
        await profile.save(update_fields=['status'])
        if status == enums.InviteStatus.REFUSED:
            return {'status': enums.InviteStatus.REFUSED}
        return await profile_get(user_id)
    except DoesNotExist as e:
        raise ProfileNotFound(
            f'Profile for provided user ID: {user_id} was not found OR Profile is not Courier',
        ) from e


@utils.save_in_history(
    request_method=enums.RequestMethods.DELETE,
    model_type='Profile',
)
async def profile_delete(user_id: int, delete: schemas.ProfileDelete) -> None:
    model = profile_types_to_models[delete.profile_type]

    try:
        profile = await model.get(user_id=user_id)
    except DoesNotExist as e:
        raise ProfileNotFound(
            f'Profile for provided user ID: {user_id} was not found',
        ) from e

    await profile.delete()
    redis_con = redis_module.get_connection()
    perm_cache_key = f"permissions:user_id:{profile.user_id}{'_profile:' + delete.profile_type}"
    await redis_con.delete(perm_cache_key)


async def courier_list(default_filter_args: list, filter_args: list):
    couriers = await ProfileCourier.filter(
        *default_filter_args,
    ).filter(*filter_args).select_related('user')
    return parse_obj_as(typing.List[schemas.CourierList], couriers)


async def courier_start_work(user_id):
    try:
        profile: ProfileCourier = await ProfileCourier.get(user_id=user_id)
    except DoesNotExist:
        raise DoesNotExist('Profile does not exist')

    profile.at_work = True
    await profile.save()


async def courier_end_work(user_id):
    try:
        profile: ProfileCourier = await ProfileCourier.get(user_id=user_id)
    except DoesNotExist:
        raise DoesNotExist('Profile does not exist')

    profile.at_work = False
    await profile.save()


async def courier_stats(partner_id: int, date: datetime.date = None):
    couriers = await ProfileCourier.filter(
        partner_id=partner_id,
        status=enums.InviteStatus.ACCEPTED.value,
    ).select_related(
        'user', 'category',
    )
    result = []
    for courier in couriers:
        data = {'courier': {
            'id': courier.id,
            'user_id': courier.user_id,
            'first_name': courier.user.first_name,
            'middle_name': courier.user.middle_name,
            'last_name': courier.user.last_name,
        }}
        if courier.category:
            data['courier'].update({
                'category_type': courier.category.item_type,
                'category_name': courier.category.name,
            })
        data.update(await get_stats(courier_id=courier.id, date=date))

        result.append(data)

    return result


async def courier_stats_get(user_id: int, partner_id, date: datetime.date = None):
    try:
        courier = await ProfileCourier.get(
            user_id=user_id,
            partner_id=partner_id,
        ).select_related('user', 'category')
        data = {
            'courier': {
                'id': courier.id,
                'first_name': courier.user.first_name,
                'middle_name': courier.user.middle_name,
                'last_name': courier.user.last_name,
                'user_id': user_id
            },
            'rates': []}
        if courier.category:
            data['courier'].update({
                'category_type': courier.category.item_type,
                'category_name': courier.category.name,
            })
        if date:
            stat = await get_stats(courier_id=courier.id, date=date)
            stat['month'] = date
            data['rates'].append(stat)
            return data

        next_month = now().replace(day=28) + datetime.timedelta(days=4)
        last_day_of_month = next_month - datetime.timedelta(days=next_month.day)
        dates = list(rrule.rrule(
            rrule.MONTHLY,
            dtstart=courier.created_at.date(),
            until=last_day_of_month.date(),
        ))
        dates.reverse()
        for date in dates:
            monthly_stat = {'month': date}
            monthly_stat.update(await get_stats(courier_id=courier.id, date=date))
            data['rates'].append(monthly_stat)

        data['total'] = await get_stats(courier_id=courier.id)
        return data

    except DoesNotExist:
        raise ProfileNotFound(
            f'Courier with given user_id: {user_id} was not found',
        )


async def get_stats(
    courier_id: int = None,
    date: datetime.date = None,
):
    data = {}

    query_objects = []
    if date:
        query_objects.append(
            Q(created_at__startswith=f'{date.year}-{date.month:02d}')
        )
    data['rate'] = 0
    rate = await models.Rate.filter(
        *query_objects,
        courier_id=courier_id,
    ).first()
    if rate:
        data['rate'] = rate.value
    data['negative_feedbacks'] = await models.Feedback.filter(
        *query_objects,
        rate__lt=5,
        status=enums.FeedbackStatus.APPROVED.value,
        order__courier_id=courier_id,
    ).count()
    data['positive_feedbacks'] = await models.Feedback.filter(
        *query_objects,
        rate=5,
        status=enums.FeedbackStatus.APPROVED.value,
        order__courier_id=courier_id,
    ).count()
    data['orders'] = await models.OrderStatuses.filter(
        *query_objects,
        id=enums.OrderStatus.DELIVERED.value,
        order__courier_id=courier_id,
    ).count()
    data['late_delivery'] = await models.OrderStatuses.filter(
        *query_objects,
        status_id=enums.OrderStatus.DELIVERED.value,
        order__courier_id=courier_id,
    ).count()

    return data


async def profile_send_magic_link(inviter_id: int, profile_type: enums.ProfileType, profile_id: int):
    domain = conf.frontend.domain
    profile = await profile_types_to_models[profile_type].get(id=profile_id)
    user_obj = await profile.user
    payload = {
        'client_id': user_obj.id,
        'email': user_obj.email,
    }
    exp = now() + datetime.timedelta(days=1)
    token = security.sign_token(payload, int(exp.timestamp()))
    magic_link = f'https://{domain}/set-password?t={token}'
    role_map = {
        enums.ProfileType.SERVICE_MANAGER: 'менеджера',
        enums.ProfileType.DISPATCHER: 'диспетчера',
        enums.ProfileType.COURIER: 'курьера',
        enums.ProfileType.BRANCH_MANAGER: 'менеджера филиала',
        enums.ProfileType.PARTNER_BRANCH_MANAGER: 'специалиста по самовывозу',
        enums.ProfileType.SORTER: 'сортировщика',
        enums.ProfileType.MANAGER: 'менеджера партнера',
        enums.ProfileType.BANK_MANAGER: 'менеджера банка',
        enums.ProfileType.SUPERVISOR: 'супервайзера',
        enums.ProfileType.LOGIST: 'логиста',
        enums.ProfileType.CALL_CENTER_MANAGER: 'специалиста колл-центра',
        enums.ProfileType.GENERAL_CALL_CENTER_MANAGER: 'расширенного специалиста колл-центра',
        enums.ProfileType.SUPPORT: 'Support',
    }
    await send_email_magic_link(
        email=user_obj.email,
        magic_link=magic_link,
        user_id=inviter_id,
        receiver_full_name=user_obj.fullname,
        receiver_role=role_map[profile_type],
    )
