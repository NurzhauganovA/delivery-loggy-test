from fastapi import Security
from tortoise.expressions import Q

from api import exceptions
from .. import auth
from .. import schemas
from ..enums import ProfileType


async def area_get_default_filter_args(
    current_user: schemas.UserCurrent = Security(auth.get_current_user)
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
        case ProfileType.BRANCH_MANAGER:
            cities = [city.id for city in current_user.profile['profile_content']['cities']]
            args.append(Q(partner_id__in=current_user.partners))
            args.append(Q(city_id__in=cities))
        case ProfileType.COURIER:
            args.append(Q(couriers__id=profile['id']))
        case ProfileType.SUPERVISOR:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                    city__country_id=profile_content['country_id'],
                )
            )
        case ProfileType.CALL_CENTER_MANAGER:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                    city__country_id=profile_content['country_id'],
                )
            )
        case ProfileType.GENERAL_CALL_CENTER_MANAGER:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                )
            )
        case ProfileType.LOGIST:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                    city__country_id=profile_content['country_id'],
                )
            )
        case ProfileType.SUPPORT:
            args.append(
                Q(
                    partner_id__in=current_user.partners,
                )
            )
        case _:
            args.append(Q(partner_id__in=current_user.partners))

    return args


async def area_validate_payload(
    area: schemas.AreaCreate,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    errors = []
    if current_user.is_superuser:
        return area
    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            if area.partner_id != profile_content['partner_id']:
                errors.append(('partner_id', 'Partner does not exist'))
        case ProfileType.BRANCH_MANAGER:
            if area.partner_id != profile_content['partner_id']:
                errors.append(('partner_id', 'Partner does not exist'))
            cities = [item.id for item in profile_content['cities']]
            if area.city_id not in cities:
                errors.append(('city_id', 'City does not exist'))
    if errors:
        raise exceptions.PydanticException(errors=errors)
    return area
