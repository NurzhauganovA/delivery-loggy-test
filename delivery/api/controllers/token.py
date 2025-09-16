from .. import auth
from .. import exceptions
from .. import security
from .. import models


async def token_obtain(
    credential: str,
    password: str,
    profile_type: str | None = None,
    profile_id: int | None = None,
):
    try:
        user = await auth.authenticate_user(credential, password)
    except auth.InvalidUserCredentials as e:
        raise exceptions.HTTPBadRequestException from e
    profiles = await models.get_all_user_profiles(user.id)
    token_schema = await auth.token_obtain(
        client_id=user.id,
        profile_type=profile_type,
        profile_id=profile_id
    )
    token_schema.profiles = profiles
    return token_schema


async def token_refresh(
    refresh_token: str,
    profile_type: str | None = None,
    profile_id: int | None = None,
):
    try:
        return await auth.token_refresh(
            refresh_token=refresh_token,
            profile_type=profile_type,
            profile_id=profile_id,
        )
    except (auth.TokenRefreshException, security.InvalidToken) as e:
        raise exceptions.HTTPBadRequestException from e


async def token_revoke(
    client_id: int,
    refresh_token: str,
    device_token: str,
):
    try:
        await auth.token_revoke(
            client_id=client_id,
            refresh_token=refresh_token,
            device_token=device_token,
        )
    except auth.TokenRevocationException as e:
        raise exceptions.HTTPBadRequestException from e
