import typing

import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth, dependencies
from ... import controllers
from ... import models
from ... import responses
from ... import schemas

router = fastapi.APIRouter()


@router.get(
    '/item/list',
    summary='Get list of items',
    response_model=typing.List[schemas.ItemGet],
    response_description='List of items',
)
async def item_get_list(
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['i:l'],
    ),
    default_filter_args: list = fastapi.Depends(
        dependencies.item_default_filter_args
    ),
    filter_args: list = fastapi.Depends(dependencies.item_list_filter_args)
):
    """Get list of items."""
    result = await controllers.item_get_list(
        default_filter_args=default_filter_args,
        filter_args=filter_args
    )
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/item/{item_id}',
    summary='Get item',
    response_model=schemas.ItemGet,
)
async def item_get(
    item_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['i:g'],
    ),
    default_filter_args: list = fastapi.Depends(
        dependencies.item_default_filter_args
    ),
):
    """Get item with provided ID."""

    result = await controllers.item_get(
        item_id,
        default_filter_args=default_filter_args
    )
    return JSONResponse(jsonable_encoder(result))


@router.post(
    '/item',
    summary='Create item',
    response_model=schemas.ItemGet,
    status_code=201,
)
async def item_create(
    payload: schemas.ItemCreate = fastapi.Depends(dependencies.item_validate_create_payload),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
) -> models.Item:
    """Create item."""
    return await controllers.item_create(
        payload=payload,
        current_user=current_user,
    )


@router.post(
    '/item/{item_id}/shipment_points',
    summary='Create shipment points',
    status_code=204,
)
async def item_shipment_points_create(
    create: schemas.ItemShipmentPointCreate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['i:u'],
    ),
    default_filter_args: list = fastapi.Depends(
        dependencies.item_default_filter_args
    ),
):
    """Create shipment points for item with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided item not found
    """
    shipmen_point_kwargs = {
        'partner_id__in': current_user.partners,
    }

    await controllers.item_shipment_points_create(
        create,
        default_filter_args,
        shipmen_point_kwargs,
    )
    return fastapi.responses.Response(status_code=201)


@router.put(
    '/item/{item_id}',
    response_model=schemas.ItemGet,
)
async def item_update(
    item_id: int,
    payload: schemas.ItemUpdate = fastapi.Depends(dependencies.item_validate_update_payload),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
):
    updated_item = await controllers.item_update(
        item_id=item_id,
        payload=payload,
        current_user=current_user,
    )

    return JSONResponse(jsonable_encoder(updated_item))


@router.patch(
    '/item/{item_id}',
    response_model=schemas.ItemGet,
)
async def item_update_partial(
    item_id: int,
    payload: schemas.ItemPartialUpdate = fastapi.Depends(dependencies.item_validate_update_payload),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
    default_filter_args: list = fastapi.Depends(dependencies.item_default_filter_args),
):
    updated_item = await controllers.item_update(
        item_id=item_id,
        payload=payload,
        current_user=current_user,
        default_filter_args=default_filter_args,
    )

    return JSONResponse(jsonable_encoder(updated_item))


@router.delete(
    '/item/delete_many',
    summary='Delete many items',
    response_description='Items deleted successfully',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseNoContent,
        ],
    ),
    status_code=204,
)
async def item_delete_many(
    item_ids: schemas.ItemIDsList,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['i:md'],
    ),
    default_filter_args: list = fastapi.Depends(
        dependencies.item_default_filter_args
    ),
) -> fastapi.responses.Response:
    """Delete items with provided IDs.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided items in ids list not found
    """
    await controllers.item_delete_many(
        item_ids,
        default_filter_args,
    )
    return fastapi.responses.Response(status_code=204)


@router.delete(
    '/item/{item_id}',
    summary='Delete an item',
    response_description='Item deleted successfully',
    status_code=204,
)
async def item_delete(
    item_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['i:d'],
    ),
    default_filter_args: list = fastapi.Depends(
        dependencies.item_default_filter_args
    ),
):
    """Delete item with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided item not found
    """

    await controllers.item_delete(
        item_id,
        default_filter_args,
    )
    return fastapi.responses.Response(status_code=204)


@router.post(
    '/item/{item_id}/cities',
    summary='Add city to item',
    response_description='City successfully added to item',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseNoContent,
        ],
    ),
    status_code=204
)
async def item_cities_add(
    item_id: int,
    city_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['i:u'],
    ),
    default_filter_args: list = fastapi.Depends(
        dependencies.item_default_filter_args
    ),
) -> fastapi.responses.Response:
    """Add city to item"""

    await controllers.item_cities_add(
        item_id, city_id,
        default_filter_args,
    )
    return fastapi.responses.Response(status_code=204)
