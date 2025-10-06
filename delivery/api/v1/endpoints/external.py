import typing

import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth
from ... import controllers
from ... import schemas
from ... import responses
from ...dependencies.order import external_order_default_filter_args
from ...modules.shipment_point.actions import ShipmentPointActions
from ...modules.shipment_point.dependecies import shipment_point_default_filter_args_external
from ...modules.shipment_point.schemas import PartnerShipmentPointFilter
from api.controllers.external_order_create import(
    external_order_create,
    get_external_order,
)
from api.dependencies.controllers import get_handle_order_status_transition_controller
from api.controllers.handle_order_status_transition import OrderStatusTransitionHandlers


router = fastapi.APIRouter()


@router.get(
    '/external/countries',
    summary='Get list of countries for external',
    response_model=typing.List[schemas.CountryGet],
    response_description='List of countries for external',
)
async def country_get_list_external(
        _: schemas.UserCurrent = fastapi.Security(
            auth.get_current_partner,
        ),
):
    """Get list of countries."""
    result = await controllers.country_get_list()
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    '/external/shipment_point',
    summary='Get list of partner shipment points',
    response_model=schemas.Page[schemas.PartnerShipmentPointGet],
    response_description='List of partner shipment points',
)
async def shipment_point_get_list_external(
    pagination_params: schemas.Params = fastapi.Depends(schemas.Params),
    default_filter_args: list = fastapi.Depends(
        shipment_point_default_filter_args_external
    ),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_partner,
    ),
    city_id: int = None,
):
    """Get list of shipment points."""
    shipment_point_action = ShipmentPointActions()
    return await shipment_point_action.shipment_point_get_list(
        default_filter_args=default_filter_args,
        pagination_params=pagination_params,
        filter_kwargs=PartnerShipmentPointFilter(
            city_id=city_id
        )
    )


# External order create 2
@router.post(
    '/external/order/create',
    summary='Create order',
    response_model=schemas.OrderGetV1,
    response_description='Created order',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def external_order_create_external(
    order: schemas.ExternalOrderCreate,
    api_key: str,
    handler: OrderStatusTransitionHandlers = fastapi.Depends(get_handle_order_status_transition_controller),
):
    order_id = await external_order_create(
        order=order,
        api_key=api_key,
        handler=handler,
    )
    order = await get_external_order(
        order_id=order_id
    )
    return order


@router.get(
    '/external/order/{order_id}/status',
    summary='Get order current status',
    response_model=schemas.OrderStatusGet,
    response_description='Order current status',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def order_get_current_status_external(
    order_id: int,
    api_key: str
) -> schemas.OrderStatusGet:
    """Returns order current status with provided ID.

    Returns 404 NOT FOUND due to the following:
    * `not_found`: provided order not found
    """
    return await controllers.order_current_status_external(
        order_id=order_id,
        api_key=api_key,
    )


@router.post(
    '/external/order/{order_id}/cancel',
    summary='Cancel order',
    response_description='Order current status',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def order_cancel_external(
    order_id: int,
    default_filter_args: list = fastapi.Depends(
        external_order_default_filter_args
    ),
    current_partner: schemas.UserCurrent = fastapi.Security(
        auth.get_current_partner,
    ),
) -> fastapi.responses.Response:
    """Cancel order.

    Returns 404 NOT FOUND due to the following:
    * `not_found`: provided order not found
    """
    await controllers.external_order_cancel(
        order_id=order_id,
        default_filter_args=default_filter_args,
        current_user=current_partner,
    )

    return fastapi.responses.Response(status_code=204)
