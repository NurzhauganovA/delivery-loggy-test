from api import auth, schemas
from .schemas import PartnerSettingUpdate
from api.enums import ProfileType
from fastapi import Security
from tortoise.expressions import Q

from api import exceptions


async def partner_setting_default_filter_args(
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
        case ProfileType.SUPERVISOR:
            args.append(Q(partner_id__in=current_user.partners))
        case _:
            raise exceptions.HTTPUnauthorizedException

    return args


async def partner_setting_validate_payload(
    setting: PartnerSettingUpdate,
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
):
    profile = current_user.profile
    profile_type = profile['profile_type']
    profile_content = profile['profile_content']
    errors = []
    if current_user.is_superuser:
        return setting
    if errors:
        raise exceptions.PydanticException(errors=errors)
    return setting
