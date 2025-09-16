from fastapi import Security, Depends
from tortoise.expressions import Q

from api import exceptions
from .. import auth
from .. import schemas
from ..enums import ProfileType, OrderType


async def item_default_filter_args(
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
) -> list:
    profile = current_user.profile
    profile_type = profile['profile_type']
    args = []
    if current_user.is_superuser:
        return args
    match profile_type:
        case ProfileType.BRANCH_MANAGER:
            cities = [city.id for city in profile['profile_content']['cities']]
            args.append(Q(cities__id__in=cities))
        case ProfileType.PARTNER_BRANCH_MANAGER:
            args.append(Q(delivery_type__iexact=f'{{{OrderType.PICKUP.value}}}'))
        case ProfileType.SUPERVISOR:
            args.append(Q(cities__country_id=profile['profile_content']['country_id']))
        case ProfileType.LOGIST:
            args.append(Q(cities__country_id=profile['profile_content']['country_id']))
        case ProfileType.CALL_CENTER_MANAGER:
            args.append(Q(cities__country_id=profile['profile_content']['country_id']))
    args.append(Q(partner_id__in=current_user.partners))
    return args


async def item_validate_create_payload(
    payload: schemas.ItemCreate,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile['profile_content']
    profile_type = current_user.profile['profile_type']

    if payload.partner_id not in current_user.partners:
        raise exceptions.HTTPBadRequestException(
            f'Partner with given ID: {payload.partner_id} was not found',
        )

    match profile_type:
        case ProfileType.BRANCH_MANAGER:
            if profile['city_id'] not in payload.cities:
                raise exceptions.HTTPBadRequestException(
                    'City with given ID is not available')

    return payload


async def item_validate_update_payload(
    payload: schemas.ItemUpdate | schemas.ItemPartialUpdate,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile['profile_content']
    profile_type = current_user.profile['profile_type']

    if payload.partner_id and payload.partner_id not in current_user.partners:
        raise exceptions.HTTPBadRequestException(
            f'Partner with given ID: {payload.partner_id} was not found',
        )

    match profile_type:
        case ProfileType.BRANCH_MANAGER:
            if payload.cities and profile['city_id'] not in payload.cities:
                raise exceptions.HTTPBadRequestException(
                    'City with given ID is not available')

    return payload


async def item_list_filter_args(
    filter_params: schemas.ItemFilter = Depends(schemas.ItemFilter),
) -> list:
    filter_params = filter_params.dict(exclude_unset=True, exclude_none=True)
    args = []

    for k, v in filter_params.items():
        args.append(Q(**{k: v}))
    return args
