# TODO: wrap return values into schemas

import fastapi.security
import tortoise.transactions
from tortoise.models import Q

from api import exceptions
from .conf import conf
from .services import sms
from . import enums
from . import models
from . import schemas
from . import security


class InvalidUserCredentials(Exception):
    """Raises when wrong user credentials were provided."""


class UserIsNotActive(Exception):
    """Raises if user is not active"""


class TokenRefreshException(Exception):
    """Raised when provided access tokens are invalid."""


class TokenRevocationException(Exception):
    """Raises when provided token was already revoked or is not present."""


def simple_auth(x_front_token: str | None = fastapi.Header(None)) -> None:
    if not x_front_token:
        raise exceptions.HTTPUnauthenticatedException('token was not provided')
    if x_front_token != conf.token.front_token:
        raise exceptions.HTTPUnauthenticatedException('invalid token was provided')


async def authenticate_user(credential: str, password: str):
    """Authenticate the user with its credentials within the system."""
    exc = InvalidUserCredentials('Wrong user credentials were provided')

    try:
        user = await models.user_get_by_email(credential)
    except models.UserNotFound as e:
        try:
            user = await models.user_get_by_phone_number(credential)
        except models.UserNotFound as e:
            raise exc from e

    password_stored = await sms.otp_service.check_otp(f"otp_{credential}")

    if (password_stored is None or password_stored != password) and not user.check_password(password):
        raise exc

    return user


async def get_current_user(
    security_scopes: fastapi.security.SecurityScopes = None,
    token: str = fastapi.Security(security.oauth2_scheme),
):
    """Get currently authorized user."""
    exc = exceptions.HTTPUnauthenticatedException(
        'Could not validate credentials',
    )
    if security_scopes is None:
        security_scopes = fastapi.security.SecurityScopes()

    if await models.RevokedToken.filter(token=token).exists():
        raise exc

    try:
        decoded_token = security.unsign_token(token)
    except security.InvalidToken:
        raise exc

    client_id = decoded_token.get('client_id')
    if client_id is None:
        raise exc

    try:
        profile_type_token = decoded_token.get('profile_type')
        profile_id_token = decoded_token.get('profile_id')
        user = await models.user_get(id=client_id, with_history=False)
        if profile_type_token and profile_id_token:
            user = await models.get_user_profile_with_info(
                user=user, profile_id=profile_id_token, profile_type=profile_type_token)
    except models.UserNotFound as e:
        raise exc from e
    is_active = user.get('is_active')
    profile_type = user.get('profile_type')
    if not (is_active or (profile_type is None or profile_type != enums.ProfileType.COURIER)):
        raise exceptions.HTTPUnauthenticatedException('User is not active')

    scopes = decoded_token.get('scopes', '').split(' ')

    if user['is_superuser']:
        return schemas.UserCurrent(**user)

    for scope in security_scopes.scopes:
        if scope not in scopes:
            raise exceptions.HTTPUnauthorizedException(
                f'Not permitted',
            )
    return schemas.UserCurrent(**user)


async def get_current_partner(api_key: str):
    token = await models.PublicApiToken.filter(token=api_key).first()
    if not token:
        raise models.PublicApiTokenNotFound('Cannot get partner with provided api key')
    partner = await models.partner_get(partner_id=token.partner_id, with_info=False)
    return schemas.PartnerGet(**partner)


async def get_scopes(client_id) -> str:
    scopes = await models.Permission.filter(
        Q(users=client_id) | Q(group_set__user_set=client_id)
    ).distinct().values_list('slug', flat=True)
    return ' '.join(scopes)


@tortoise.transactions.atomic()
async def token_obtain(
    client_id: int,
    profile_type: str = None,
    profile_id: int = None,
):
    """Obtain new auth token."""
    payload = {
        'client_id': client_id,
        'scopes': await get_scopes(client_id),
    }
    if profile_type and profile_id:
        payload['profile_type'] = profile_type
        payload['profile_id'] = profile_id
    issued_access_token = security.issue_access_token(payload=payload)
    refresh_payload = {
        'client_id': client_id,
    }
    if profile_type and profile_id:
        refresh_payload['profile_type'] = profile_type
        refresh_payload['profile_id'] = profile_id
    issued_refresh_token = security.issue_refresh_token(payload=refresh_payload)
    return schemas.TokenGet(
        access_token=issued_access_token.token,
        refresh_token=issued_refresh_token.token,
        token_type=issued_access_token.token_type,
    )


async def token_refresh(
    refresh_token: str,
    profile_type: str | None = None,
    profile_id: int | None = None,
):
    """Refresh previously obtained token."""
    exc = TokenRefreshException('invalid token was provided')

    try:
        decoded_token = security.unsign_token(refresh_token)
    except security.InvalidToken:
        raise exc

    token_revoked = (await models.token_get(token=refresh_token)) is not None
    if token_revoked:
        raise exc

    client_id = decoded_token['client_id']

    payload = {
        'client_id': client_id,
        'scopes': await get_scopes(client_id),
    }
    if profile_type and profile_id:
        payload['profile_type'] = profile_type
        payload['profile_id'] = profile_id
    else:
        payload['profile_type'] = decoded_token.get('profile_type')
        payload['profile_id'] = decoded_token.get('profile_id')

    issued_access_token = security.issue_access_token(payload=payload)

    return schemas.TokenGet(
        access_token=issued_access_token.token,
        refresh_token=refresh_token,
        token_type=issued_access_token.token_type,
    )


async def token_revoke(
    client_id: int,
    refresh_token: str,
    device_token: str,
):
    """Revoke refresh token."""
    exc = TokenRevocationException('Invalid refresh token')
    effective_client_id = security.extract_client_id_from_signed_token(refresh_token)
    if effective_client_id != client_id:
        raise exc
    await models.token_revoke(refresh_token)
    await models.FCMDevice.filter(id=device_token, user_id=client_id).delete()
