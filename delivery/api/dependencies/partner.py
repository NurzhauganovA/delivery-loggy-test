from fastapi import Security, Depends
from tortoise.expressions import Q

from .. import auth
from .. import schemas
from ..enums import ProfileType


async def partner_default_filter_args(
    current_user: schemas.UserCurrent = Security(auth.get_current_user),
) -> list:
    profile = current_user.profile
    profile_type = profile['profile_type']
    args = []
    if current_user.is_superuser:
        return args
    match profile_type:
        case ProfileType.SERVICE_MANAGER:
            args.append(Q(id__in=current_user.partners))
        case ProfileType.MANAGER:
            args.append(Q(id__in=current_user.partners))
    return args
