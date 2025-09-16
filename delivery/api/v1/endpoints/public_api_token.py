import typing

import fastapi

from ... import auth
from ... import controllers
from ... import responses
from ... import schemas


router = fastapi.APIRouter()


@router.get(
    '/public_api_token/my',
    summary='Get public api token',
    response_model=schemas.PublicApiTokenGet,
    response_description='City',
)
async def public_api_token_get(
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        # scopes=['c:g'],
    ),
):
    """Get public api token with provided partner."""
    return await controllers.public_api_token_get(current_user)


@router.post(
    '/public_api_token',
    summary='Crete public api token',
    response_model=schemas.PublicApiTokenGet,
    response_description='Created public api token',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def public_api_token_create(
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        # scopes=['at:c'],
    ),
):
    """Create public api token.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner does not exist
    """
    return await controllers.public_api_token_create(current_user=current_user)