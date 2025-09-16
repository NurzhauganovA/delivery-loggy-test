import typing

import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth
from ... import controllers
from ... import schemas
from api.common import schema_base


router = fastapi.APIRouter()


@router.get(
    '/status/list/default',
    summary='Get list of default statuses',
    response_model=typing.List[schemas.StatusGet],
    response_description='List of default statuses',
)
async def system_status_get_list(
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Get list of default statuses."""
    result = await controllers.status_get_default()
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/status/{status_id}',
    summary='Get status',
    response_model=schemas.StatusGet,
    response_description='Status',
)
async def status_get(
    status_id: int,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Get status with provided ID"""
    result = await controllers.status_get(status_id)
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/status/list/{partner_id}',
    summary='Get list of statuses',
    response_model=schemas.Page[schemas.StatusGet],
    response_description='List of statuses',
)
async def status_get_list(
    partner_id: int,
    pagination_params: schemas.Params = fastapi.Depends(schemas.Params),
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Get list of statuses."""
    result = await controllers.status_get_list(pagination_params, partner_id)
    return JSONResponse(jsonable_encoder(result))


@router.post(
    '/status',
    summary='Create status',
    response_model=schemas.StatusGet,
    response_description='Created status',
)
async def status_create(
    status: schemas.StatusCreate,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Create status.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: status not found
    """
    result = await controllers.status_create(status)
    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/status/{status_id}',
    summary='Update a status',
    response_model=schemas.StatusGet,
    response_description='Updated status',
)
async def status_update(
    status_id: int,
    update: schemas.StatusUpdate,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Update status with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided status not found
    """
    result = await controllers.status_update(status_id, update)
    return JSONResponse(jsonable_encoder(result))


@router.patch(
    '/status/{status_id}',
    summary='Partial Update a status',
    response_model=schemas.StatusGet,
    response_description='Updated status',
)
async def status_partial_update(
    status_id: int,
    update: schema_base.partial(schemas.StatusUpdate),
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Partial Update status with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided status not found
    """
    result = await controllers.status_update(status_id, update)
    return JSONResponse(jsonable_encoder(result))


@router.delete(
    '/status/{status_id}',
    summary='Delete a status',
    response_description='Status deleted successfully',
    status_code=204,
)
async def status_delete(
    status_id: int,
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Delete status with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided status not found
    """
    await controllers.status_delete(status_id)
    return fastapi.responses.Response(status_code=204)
