from fastapi import Security, Depends
from tortoise.expressions import Q, Subquery

from api import auth
from api.enums import ProfileType
from api.schemas import UserCurrent
from .schemas import CityFilter
from ...models import Item


async def city_default_filter_args(
    current_user: UserCurrent = Security(auth.get_current_user),
) -> list:
    profile = current_user.profile
    profile_type = profile['profile_type']

    args = []

    if current_user.is_superuser:
        return args

    match profile_type:
        case ProfileType.BRANCH_MANAGER:
            cities = [city.id for city in profile['profile_content']['cities']]
            args.append(Q(id__in=cities))

    return args


async def city_filter_kwargs(
    current_user: UserCurrent = Security(auth.get_current_user),
    filter_schema: CityFilter = Depends(CityFilter),
) -> dict:
    filter_kwargs = filter_schema.dict(exclude_unset=True, exclude_none=True)
    if partner_id := filter_kwargs.pop('partner_id', None):
        if partner_id in current_user.partners:
            filter_kwargs['id__in'] = Subquery(
                Item.filter(partner_id=partner_id).values_list('cities__id', flat=True),
            )
        else:
            filter_kwargs['id__in'] = Subquery(
                Item.filter(partner_id__in=current_user.partners).values_list('cities__id', flat=True),
            )

    return filter_kwargs
