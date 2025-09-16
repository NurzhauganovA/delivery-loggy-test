import fastapi.security.oauth2
from loguru import logger

from ... import auth
from ... import controllers
from ... import dependencies
from ... import responses
from ... import schemas

router = fastapi.APIRouter()


@router.post(
    '/token',
    summary='Obtain OAuth2 token',
    response_model=schemas.TokenGet,
    response_description='Obtained token',
    responses=responses.generate_responses([responses.APIResponseUnauthenticated]),
)
async def token_obtain(
    payload: dict = fastapi.Depends(dependencies.token_validate_payload),
):
    """Obtain `OAuth2` token by providing valid user credentials.

    The values for standard fields were redefined, meaning that
    `username` is for phone number and `password` is for OTP.

    - `grant_type`: Must always be set to 'password'
    - `username`: Provide phone number
    - `password`: Provide OTP

    Obtained `access_token` may be later used to access protected resources,
    use appropriate `HTTP` header:

    ```
    Authorization: Bearer obtained_access_token
    ```

    Returns 401 UNAUTHENTICATED due to the following statuses:
    * `unauthenticated`: invalid user credentials
    """
    result = await controllers.token_obtain(**payload)
    return result


@router.post(
    '/token/refresh',
    summary='Refresh OAuth2 token',
    response_model=schemas.TokenGet,
    response_description='Refreshed token',
    responses=responses.generate_responses([responses.APIResponseBadRequest]),
)
async def token_refresh(
    profile_id: int | None = None,
    profile_type: str | None = None,
    refresh_token: str = fastapi.Form(...),
):
    """Refresh `OAuth2` access token by providing valid refresh token.

    - `grant_type`: Must always be set to 'refresh_token'
    - `refresh_token`: Valid refresh token

    Obtained `access_token` may be later used to access protected resources,
    use appropriate `HTTP` header:

    ```
    Authorization: Bearer obtained_access_token
    ```

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: caused by any token refresh related error
    """
    return await controllers.token_refresh(
        refresh_token=refresh_token,
        profile_type=profile_type,
        profile_id=profile_id,
    )


@router.post(
    '/token/revoke',
    summary='Revoke OAuth2 token',
    response_description='Token revoked successfully',
)
async def token_revoke(
    refresh_token: str = fastapi.Form(...),
    device_token: str | None = fastapi.Form(None),
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Revoke `OAuth2` token by providing revocable token.

    - `token`: Revocable token (access or refresh token)
    - `token_type_hint`: Used to specify which token type is going to be revoked. If not set,
    this will be determinated automatically.

    If access token was provided, revokes it. If refresh token was provided,
    revokes it and all the corresponding access tokens.

    Returns 400 BAD REQUEST due to the following statuses:
    * `token_revoke_error` - Any error related to token revocation

    """
    await controllers.token_revoke(
        client_id=current_user.id,
        refresh_token=refresh_token,
        device_token=device_token,
    )
