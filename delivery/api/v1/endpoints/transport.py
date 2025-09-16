import fastapi

from ... import auth
from ... import controllers
from ... import responses
from ... import schemas


router = fastapi.APIRouter()


@router.get(
    '/transport/{transport_id}',
    summary='Get transport',
    response_model=schemas.TransportGet,
    response_description='Transport',
)
async def transport_get(
    transport_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Get transport with provided ID."""
    return await controllers.transport_get(transport_id)


@router.post(
    '/transport',
    summary='Create transport',
    response_model=schemas.TransportGet,
    response_description='Created transport',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def transport_create(
    transport: schemas.TransportCreate,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Create transport.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: transport not found
    """
    return await controllers.transport_create(transport)


@router.put(
    '/transport/{transport_id}',
    summary='Update transport',
    response_model=schemas.TransportGet,
    response_description='Updated transport',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def transport_update(
    transport_id: int,
    transport: schemas.TransportUpdate,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Update transport with provied ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided transport not found
    """
    return await controllers.transport_update(transport_id, transport)


@router.delete(
    '/transport/{transport_id}',
    summary='Delete transport',
    response_description='Transport deleted successfully',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseNoContent,
        ],
    ),
    status_code=204,
)
async def transport_delete(
    transport_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Delete transport with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided transport not found
    """
    await controllers.transport_delete(transport_id)
    return fastapi.Response(status_code=204)
