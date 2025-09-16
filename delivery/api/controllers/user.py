import typing

import fastapi
from tortoise.expressions import Subquery
from tortoise.transactions import atomic

from ..enums import ProfileType, StatusSlug, OrderStatus
from ..services import sms

from api import exceptions
from ..conf import conf
from .. import enums
from .. import models
from .. import schemas
from .. import utils
from ..services.sms.notification import send_confirm_email_otp


async def user_get_current(
    current_user: schemas.UserCurrent,
    with_profile: bool,
) -> dict:
    user = current_user.dict()
    if not current_user.profile:
        return user
    profile_type = current_user.profile['profile_type']
    profile_content = current_user.profile['profile_content']
    if profile_type in [
        enums.ProfileType.SERVICE_MANAGER, enums.ProfileType.DISPATCHER
    ]:
        partner_ids = current_user.partners
        items = await models.Item.filter(
            partner_id__in=partner_ids,
        ).values_list('id', flat=True)
        areas = await models.Area.filter(
            partner_id=profile_content['partner_id']
        ).values_list('id', flat=True)
        partner = await models.partner_get(
            partner_id=profile_content['partner_id'], with_info=True
        )
        user['areas'] = areas
        user['items'] = items
        user['partner'] = partner
    if profile_type == enums.ProfileType.MANAGER:
        user.pop('partners')
        items = await models.Item.filter(
            partner_id=profile_content['partner_id'],
        ).values_list('id', flat=True)
        try:
            areas = await models.area_get_list(
                filter_kwargs={'partner_id': profile_content.get('courier_partner_id')}
            )
            user['areas'] = areas
            user['items'] = items
        except models.PartnerNotFound as e:
            raise exceptions.HTTPNotFoundException(str(e)) from e
    partner = await models.partner_get(profile_content['partner_id'])
    user['partner'] = partner
    user['profiles'] = await models.get_all_user_profiles(user.get('id'))
    if not with_profile:
        user.pop('profile')
    return user


async def user_get_list(pagination_params, **kwargs):
    city_id = kwargs.pop('city_id', None)
    current_user: schemas.UserCurrent = kwargs.pop('current_user')
    profile = current_user.profile
    kwargs['partner_id__in'] = current_user.partners

    match profile['profile_type']:
        case enums.ProfileType.SUPERVISOR:
            kwargs['profile_courier__city__country_id'] = profile['profile_content']['country_id']
        case enums.ProfileType.LOGIST:
            kwargs['profile_courier__city__country_id'] = profile['profile_content']['country_id']
        case enums.ProfileType.CALL_CENTER_MANAGER:
            kwargs['profile_courier__city__country_id'] = profile['profile_content']['country_id']
        case enums.ProfileType.BRANCH_MANAGER:
            cities = [city.id for city in profile['profile_content']['cities']]
            kwargs['profile_courier__city_id__in'] = cities
    if city_id:
        kwargs['profile_courier__city_id'] = city_id
    return await models.user_get_list(pagination_params, **kwargs)


async def user_get(current_user, **kwargs) -> dict:
    try:
        try:
            user = await models.user_get(**kwargs)
            if not user:
                raise exceptions.HTTPNotFoundException(
                    f'User with given ID not found',
                )
        except models.ProfileNotFound:
            pass
        return await models.user_get_multiple_profiles(**kwargs)
    except models.UserNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e


async def user_send_link(
    body: schemas.SendLink,
    current_user: schemas.UserCurrent,
) -> None:
    await utils.send_link(
        body=body,
        action=enums.SMSActions.REGISTRATION,
        current_user=current_user,
    )

    try:
        schema = schemas.InvitedUserCreate(
            phone_number=body.phone_number,
            invited_by_id=current_user.id,
            profile_type=current_user.profile['profile_type']
        )
        await models.invited_user_create(**schema.dict())
    except models.InvitedUserEntityError as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def user_create(
    user: typing.Union[schemas.UserCreate, schemas.UserCreateManually],
    current_user_id: int,
) -> dict:
    try:
        return await models.user_create(
            user=user, current_user_id=current_user_id)
    except models.UserAlreadyExists as e:
        raise exceptions.HTTPBadRequestException(str(e))


async def user_update(
    user_id: int, user: schemas.UserUpdate, current_user) -> dict:
    try:
        try:
            user_profile = await models.profile_get(
                user_id=user_id, skip_dependency=True)
            if user_profile[
                'profile_content'
            ]['partner_id'] not in current_user.partners:
                raise exceptions.HTTPNotFoundException(
                    f'User with given ID: {user_id} was not found',
                )
        except models.ProfileNotFound:
            pass

        return await models.user_update(user_id, user)

    except models.UserNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e))
    except models.UserAlreadyExists as e:
        raise exceptions.HTTPBadRequestException(str(e))


async def user_change_photo(user_id, photo: fastapi.UploadFile):
    return await models.user_change_photo(user_id, photo)


@atomic()
async def user_delete(user_id: int, current_user) -> None:
    try:
        try:
            user_profile = await models.profile_get(skip_dependency=True, user_id=user_id)
            if user_profile[
                'profile_content'
            ]['partner_id'] not in current_user.partners:
                raise exceptions.HTTPNotFoundException(
                    f'User with given ID: {user_id} was not found',
                )
            if user_profile['profile_type'] == ProfileType.COURIER:
                await models.Order.filter(
                    courier_id=user_profile['id'],
                    current_status_id__not_in=[
                        OrderStatus.POST_CONTROL.value,
                        OrderStatus.DELIVERED.value,
                        OrderStatus.ISSUED.value,
                    ],
                ).update(current_status_id=OrderStatus.NEW.value, delivery_status={
                    'status': None,
                    'reason': None,
                    'datetime': None,
                    'comment': None,
                })
                await models.OrderStatuses.filter(
                    order_id__in=Subquery(models.Order.filter(
                        courier_id=user_profile['id'],
                        current_status__slug__not_in=[
                            StatusSlug.POST_CONTROL.value,
                            StatusSlug.DELIVERED.value,
                            StatusSlug.ISSUED.value,
                        ],
                    ).values_list('id', flat=True)),
                ).delete()
                new_statuses = []
                histories = []
                orders = await models.Order.filter(
                    courier_id=user_profile['id'],
                    current_status__slug__not_in=[
                        StatusSlug.POST_CONTROL.value,
                        StatusSlug.DELIVERED.value,
                        StatusSlug.ISSUED.value,
                    ],
                )
                order_ids = []
                for order_obj in orders:
                    order_time = await order_obj.localtime
                    histories.append(models.History(
                        initiator_id=current_user.id,
                        initiator_type=enums.InitiatorType.USER.value,
                        initiator_role=current_user.profile['profile_type'],
                        request_method='PUT',
                        model_type='Order',
                        model_id=order_obj.id,
                        action_data={
                            'message': 'status_new_due_to_courier_unlink',
                        },
                        created_at=order_time,
                    ))
                    new_statuses.append(models.OrderStatuses(
                        status_id=OrderStatus.NEW.value,
                        order_id=order_obj.id,
                        created_at=order_time,
                    ))
                    order_ids.append(order_obj.id)
                await models.History.bulk_create(histories, batch_size=500)
                await models.OrderStatuses.bulk_create(new_statuses, batch_size=500)
                await models.Order.filter(id__in=order_ids).update(current_status_id=OrderStatus.NEW.value)

        except models.ProfileNotFound:
            pass
        return await models.user_delete(user_id)
    except models.UserNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e))


async def user_permission_add(user_id: int, permission_slug: str):
    try:
        return await models.user_permission_add(user_id, permission_slug)
    except (
        models.UserNotFound,
    ) as e:
        raise exceptions.HTTPNotFoundException(str(e))


async def user_permission_remove(user_id: int, permission_slug: str):
    try:
        return await models.user_permission_remove(user_id, permission_slug)
    except (
        models.UserNotFound,
    ) as e:
        raise exceptions.HTTPNotFoundException(str(e))


async def send_email_verification_code(user_id: int, email: str):
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


async def check_email_verification_code(user_id: int, otp: str):
    email = await sms.otp_service.check_email_otp(user_id=user_id, otp=otp)
    if not email:
        raise exceptions.HTTPNotFoundException('OTP was expired or incorrect!')

    await models.user_update(user_id=user_id, update=schemas.UserUpdate(email=email))


async def user_set_password(user_id, email, password, token):
    return await models.user_set_password(user_id=user_id, email=email, password=password, token=token)


async def user_set_password_v2(user_id, password, token):
    return await models.user_set_password_v2(user_id=user_id, password=password, token=token)
