from .. import exceptions
from .. import models
from .. import schemas
from .. import enums


async def public_api_token_get(current_user) -> schemas.PublicApiTokenGet:
    profile = current_user.profile
    if profile['profile_type'] in [
        enums.ProfileType.MANAGER,
    ]:
        return await models.public_api_token_get(partner_id=profile['profile_content']['partner_id'])


async def public_api_token_create(current_user) -> schemas.PublicApiTokenGet:
    try:
        profile = current_user.profile
        if profile['profile_type'] in [
            enums.ProfileType.MANAGER,
        ]:
            return await models.public_api_token_create(
                partner_id=profile['profile_content']['partner_id']
            )
        raise exceptions.HTTPUnauthorizedException(
            'Create token may only partner manager'
        )
    except (
            models.PartnerNotFound,
            models.PublicApiTokenAlreadyExists,
    ) as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e

