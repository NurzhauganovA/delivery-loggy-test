# TODO: Add unique constraint on address
import typing

import fastapi
from starlette.responses import Response

from ... import auth
from ... import controllers
from ... import responses
from ... import schemas
from ...modules.delivery_point.schemas import DeliveryPointGet

router = fastapi.APIRouter()


@router.get(
    '/place/list',
    summary='Get list of places',
    response_model=typing.List[schemas.PlaceGet],
    response_description='List of places',
)
async def place_get_list(
) -> list:
    """Get list of places."""
    return await controllers.place_get_list()


@router.get(
    '/place/{place_id}',
    summary='Get place',
    response_model=schemas.PlaceGet,
    response_description='Place',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def place_get(
    place_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Get place with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided place not found
    """
    return await controllers.place_get(place_id, current_user=current_user)


@router.post(
    '/place',
    summary='Create place',
    response_model=DeliveryPointGet,
    response_description='Created place',
)
async def place_create(
    place: schemas.PlaceCreate,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Create place.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: entity does not exist
    """
    return await controllers.place_create(place, current_user=current_user)


@router.put(
    '/place/{place_id}',
    summary='Update place',
    response_model=schemas.PlaceGet,
    response_description='Updated place',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def place_update(
    place_id: int,
    update: schemas.PlaceUpdate,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> dict:
    """Update place with provided ID.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: entity does not exist

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided place not found
    """
    return await controllers.place_update(place_id, update, current_user=current_user)


@router.delete(
    '/place/{place_id}',
    summary='Delete place',
    response_description='Place deleted successfully',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseNoContent,
        ],
    ),
    status_code=204,
)
async def place_delete(
    place_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> Response:
    """Delete place with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided place not found
    """
    await controllers.place_delete(place_id, current_user=current_user)
    return fastapi.responses.Response(status_code=204)
