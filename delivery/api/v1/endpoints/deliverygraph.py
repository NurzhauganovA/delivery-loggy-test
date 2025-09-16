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
    '/deliverygraph/list/default',
    summary='Get default delivery graph',
    response_model=typing.List[schemas.DeliveryGraphGet],
    response_description='Default delivery graph list',
)
async def system_deliverygraph_list(
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['dg:dl']
    ),
):
    """Get default delivery graphs"""
    result = await controllers.deliverygraph_default_get()
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/deliverygraph/{deliverygraph_id}',
    summary='Get delivery graph',
    response_model=schemas.DeliveryGraphGet,
    response_description='Delivery graph',
)
async def deliverygraph_get(
    deliverygraph_id: int,
    # current_user: schemas.UserCurrent = fastapi.Security(
    #     auth.get_current_user,
    #     scopes=['dg:g'],
    # ),
):
    """Get delivery graph with provided ID"""
    result = await controllers.deliverygraph_get(
        deliverygraph_id,
        partner_id=114,
    )
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/deliverygraph/list/{partner_id}',
    summary='Get list of delivery graphs',
    response_model=typing.List[schemas.DeliveryGraphGet],
    response_description='List of delivery graphs',
)
async def deliverygraph_get_list(
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['dg:l'],
    ),
):
    """Get list of delivery graphs."""
    result = await controllers.deliverygraph_get_list(
        partner_id=current_user.partners[0],
    )
    return JSONResponse(jsonable_encoder(result))


@router.post(
    '/deliverygraph',
    summary='Create delivery graph',
    response_model=schemas.DeliveryGraphGet,
    response_description='Created delivery graph',
)
async def deliverygraph_create(
    deliverygraph: schemas.DeliveryGraphCreate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['dg:c'],
    ),
):
    """Create delivery graph.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: delivery graph not found
    """
    result = await controllers.deliverygraph_create(
        deliverygraph=deliverygraph,
        partner_id=current_user.partners[0],
    )
    return JSONResponse(jsonable_encoder(result))


@router.patch(
    '/deliverygraph/{deliverygraph_id}',
    summary='Partial update a delivery graph',
    response_model=schemas.DeliveryGraphGet,
    response_description='Partially updated delivery graph',
)
async def deliverygraph_partial_update(
    deliverygraph_id: int,
    update: schema_base.partial(schemas.DeliveryGraphUpdate),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['dg:u'],
    )
):
    result = await controllers.deliverygraph_update(
        deliverygraph_id, update,
        partner_id=current_user.partners[0],
    )
    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/deliverygraph/{deliverygraph_id}',
    summary='Update a delivery graph',
    response_model=schemas.DeliveryGraphGet,
    response_description='Updated delivery graph',
)
async def deliverygraph_update(
    deliverygraph_id: int,
    update: schemas.DeliveryGraphUpdate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['dg:u'],
    ),
):
    """Update delivery graph with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided delivery graph not found
    """
    result = await controllers.deliverygraph_update(
        deliverygraph_id, update,
        partner_id=current_user.partners[0],
    )
    return JSONResponse(jsonable_encoder(result))


@router.delete(
    '/deliverygraph/{deliverygraph_id}',
    summary='Delete a delivery graph',
    response_description='Delivery graph deleted successfully',
    status_code=204,
)
async def deliverygraph_delete(
    deliverygraph_id: int,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['dg:d'],
    ),
):
    """Delete delivery graph with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided delivery graph not found
    """
    await controllers.deliverygraph_delete(
        deliverygraph_id,
        partner_id=current_user.partners[0],
    )
    return fastapi.responses.Response(status_code=204)
