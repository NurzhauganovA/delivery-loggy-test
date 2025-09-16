from datetime import datetime

from fastapi import Depends, Security
from tortoise.expressions import Q
from tortoise.timezone import now

from .. import schemas, models, auth
from ..enums import ProfileType


async def statistics_filter_args(
        filter_params: schemas.StatisticsFilter = Depends(schemas.StatisticsFilter),
):
    filter_params = filter_params.dict(exclude_unset=True, exclude_none=True)
    if filter_params.get('from_date') and filter_params.get('to_date'):
        range_dates = [
            filter_params.pop('from_date').replace(hour=00, minute=00),
            filter_params.pop('to_date').replace(hour=23, minute=59)
        ]
    else:
        order = await models.Order.all_objects.order_by('created_at').first()
        range_dates = [order.created_at, now()]

    filter_params['created_at__range'] = range_dates

    return filter_params


async def courier_statistics_default_filter_string(
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
) -> str:
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    filter_string = ''

    if current_user.is_superuser:
        return filter_string

    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            partner_ids = ", ".join(map(str, current_user.partners))
            filter_stmt = (f'AND courier_id IN ('
                           f'SELECT "id" FROM "profile_courier"'
                           f' WHERE "partner_id" IN ({partner_ids}))')
            filter_string += filter_stmt
        case ProfileType.DISPATCHER:
            partner_ids = ", ".join(map(str, current_user.partners))
            filter_stmt = (f'AND courier_id IN ('
                           f'SELECT "id" FROM "profile_courier"'
                           f' WHERE "partner_id" IN ({partner_ids}))')
            filter_string += filter_stmt
        case ProfileType.BRANCH_MANAGER:
            partner_ids = ", ".join(map(str, current_user.partners))
            city_ids = ", ".join(map(str, profile_content["cities"]))
            filter_stmt = (f'AND courier_id IN ('
                           f'SELECT "id" FROM "profile_courier"'
                           f' WHERE "partner_id" IN ({partner_ids} AND city_id IN ({city_ids}))')
            filter_string += filter_stmt
        case ProfileType.SUPERVISOR:
            partner_ids = ", ".join(map(str, current_user.partners))
            filter_stmt = (f'AND courier_id IN ('
                           f'SELECT "id" FROM "profile_courier"'
                           f' WHERE "partner_id" IN ({partner_ids})'
                           f' AND city_id IN (select id from "city" where country_id={profile_content["country_id"]}))'
                           )
            filter_string += filter_stmt
        case ProfileType.LOGIST:
            partner_ids = ", ".join(map(str, current_user.partners))
            filter_stmt = (f'AND courier_id IN ('
                           f'SELECT "id" FROM "profile_courier"'
                           f' WHERE "partner_id" IN ({partner_ids})'
                           f' AND city_id IN (select id from "city" where country_id={profile_content["country_id"]}))'
                           )
            filter_string += filter_stmt
        case _:
            filter_string += 'AND courier_id = -1'

    return filter_string


async def courier_statistics_default_filter_args(
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
) -> list:
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    args = []
    if current_user.is_superuser:
        return args

    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            args.append(Q(partner_id__in=current_user.partners))
        case ProfileType.BANK_MANAGER:
            args.append(Q(partner_id__in=current_user.partners, idn__isnull=False))
        case ProfileType.DISPATCHER:
            args.append(
                Q(partner_id__in=current_user.partners))
        case ProfileType.BRANCH_MANAGER:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                    city_id__in=profile_content['cities'],
                )
            )
        case ProfileType.COURIER:
            args.append(Q(id=current_user.profile['id']))
        case ProfileType.SUPERVISOR:
            args.append(Q(
                partner_id__in=current_user.partners,
                city__country_id=profile_content['country_id'],
            ))
        case ProfileType.LOGIST:
            args.append(Q(
                partner_id__in=current_user.partners,
                city__country_id=profile_content['country_id'],
            ))
        case _:
            args.append(Q(partner_id__in=current_user.partners))

    return args


async def resolve_courier_statistics_filter(
    query_filters: schemas.CourierStatFilter = Depends(),
    default_filters: str = Depends(courier_statistics_default_filter_string),
):
    resolved_filter = ''
    resolved_filter += default_filters
    courier = await models.ProfileCourier.filter(id=query_filters.courier_id).first()
    from_date = courier.created_at if courier else datetime(2022, 12, 15)
    resolved_filter += query_filters.to_string(from_date)
    if resolved_filter[:3].lower() == 'and':
        resolved_filter = 'WHERE' + resolved_filter[3:]
    return resolved_filter


async def resolve_courier_progress_filter(
    query_filters: schemas.CourierProgressFilter = Depends(),
):
    courier = await models.ProfileCourier.filter(id=query_filters.courier_id).first()
    from_date = courier.created_at if courier else datetime(2022, 12, 15)
    resolved_filter = query_filters.to_string(from_date)

    return resolved_filter


async def heatmap_filter_args(
        filter_params: schemas.StatisticsFilter = Depends(schemas.StatisticsFilter),
        current_user: schemas.UserCurrent = Security(auth.get_current_user)
):
    filter_params = filter_params.dict(exclude_unset=True, exclude_none=True)
    filter_params['partner_id__in'] = current_user.partners
    return filter_params
