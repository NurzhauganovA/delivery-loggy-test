from fastapi import Depends
from fastapi import Security
from tortoise.models import Q

from api.auth import get_current_user
from api.schemas import CourierFilter
from api.schemas import UserCurrent
from api.enums import ProfileType


async def get_courier_default_filter_args(
    user: UserCurrent = Security(get_current_user),
):
    profile = user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']

    args = []

    if user.is_superuser:
        return args
    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            args.append(
                Q(partner_id__in=user.partners)
            )
        case ProfileType.DISPATCHER:
            args.append(
                Q(partner_id__in=user.partners)
            )
        case ProfileType.MANAGER:
            args.append(
                Q(partner_id__in=user.partners)
            )
        case ProfileType.BRANCH_MANAGER:
            args.append(
                Q(
                    partner_id__in=user.partners,
                    city_id__in=[city.id for city in profile_content['cities']]
                )
            )
        case ProfileType.SUPERVISOR:
            args.append(
                Q(
                    partner_id__in=user.partners,
                    city__country=profile_content['country_id']
                )
            )
        case ProfileType.LOGIST:
            args.append(
                Q(
                    partner_id__in=user.partners,
                    city__country_id=profile_content['country_id'],
                )
            )
        case ProfileType.CALL_CENTER_MANAGER:
            args.append(
                Q(
                    partner_id__in=user.partners,
                    city__country=profile_content['country_id']
                )
            )
        case ProfileType.GENERAL_CALL_CENTER_MANAGER:
            args.append(Q(partner_id__in=user.partners))
        case ProfileType.SUPPORT:
            args.append(Q(partner_id__in=user.partners))
        case _:
            args.append(Q(id=-1))

    return args


async def get_courier_filter_args(
    payload: CourierFilter = Depends(CourierFilter)
):
    args = []

    payload_dict = payload.dict(exclude_unset=True, exclude_none=True)
    for k, v in payload_dict.items():
        args.append(Q(**{k: v}))

    return args
