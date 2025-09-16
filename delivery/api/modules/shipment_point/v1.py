import typing

import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from api import schemas, auth, responses
from fastapi_pagination.bases import AbstractPage

from .schemas import *
from .dependecies import (
    shipment_point_validate_payload, shipment_point_validate_bulk_payload,
    shipment_point_default_filter_args,
)

from .actions import ShipmentPointActions

router = fastapi.APIRouter()


@router.post(
    '/shipment_point/bulk',
    summary='Create shipment points for partner in bulk',
    response_description='Shipment points created for Partner',
)
async def partner_shipment_point_bulk_create(
    shipment_points: typing.List[PartnerShipmentPointCreate] = fastapi.Depends(
        shipment_point_validate_bulk_payload
    ),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['sp:c'],
    ),
):
    """Create shipment points for the partner with given ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = ShipmentPointActions(user=_)
    await actions.shipment_point_create_in_bulk(
        shipment_points=shipment_points
    )

    return fastapi.responses.Response(status_code=201)


@router.post(
    '/shipment_point',
    summary='Create shipment point for partner',
    response_description='Shipment points created for Partner',
)
async def partner_shipment_point_create(
    shipment_point: PartnerShipmentPointCreate = fastapi.Depends(
        shipment_point_validate_payload
    ),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['sp:c'],
    ),
):
    """Create shipment point for the partner with given ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = ShipmentPointActions(user=_)
    await actions.shipment_point_create(
        shipment_point=shipment_point
    )

    return fastapi.responses.Response(status_code=201)


@router.get(
    '/shipment_point/list',
    summary='Get list of partners shipment points',
    response_model=schemas.Page[schemas.PartnerShipmentPointGet],
    response_description='List of partner shipment_points',
)
async def shipment_point_get_list(
    filter_kwargs: schemas.ShipmentPointFilter = fastapi.Depends(PartnerShipmentPointFilter),
    pagination_params: schemas.Params = fastapi.Depends(schemas.Params),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['p:l']
    ),
    default_filter_args: list = fastapi.Depends(
        shipment_point_default_filter_args
    ),
) -> AbstractPage[PartnerShipmentPointGet]:
    """Get list of partner shipment points and courier_partner shipment points"""
    actions = ShipmentPointActions()
    return await actions.shipment_point_get_list(
        pagination_params=pagination_params,
        default_filter_args=default_filter_args,
        filter_kwargs=filter_kwargs,
    )


@router.get(
    '/shipment_point/{shipment_point_id}',
    summary='Get shipment point',
    response_model=schemas.PartnerShipmentPointGet,
    response_description='List of partner shipment_points',
)
async def shipment_point_get(
    shipment_point_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['p:l']
    ),
    default_filter_args: list = fastapi.Depends(
        shipment_point_default_filter_args
    ),
):
    """Get list of partner shipment points and courier_partner shipment points"""
    actions = ShipmentPointActions()
    result = await actions.shipment_point_get(
        default_filter_args=default_filter_args,
        shipment_point_id=shipment_point_id
    )
    return JSONResponse(content=jsonable_encoder(result))


@router.patch(
    '/shipment_point/{shipment_point_id}',
    summary='Update shipment point with given ID',
    response_description='Shipment point updated',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def partner_shipment_point_partial_update(
    shipment_point_id: int,
    update: PartnerShipmentPointUpdate = fastapi.Depends(
        shipment_point_validate_payload
    ),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['sp:u'],
    ),
    default_filter_args: list = fastapi.Depends(
        shipment_point_default_filter_args
    ),
) -> fastapi.Response:
    """Update partner shipment point with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = ShipmentPointActions(user=_)
    await actions.shipment_point_update(
        shipment_point_id=shipment_point_id,
        update=update,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=201)


@router.delete(
    '/shipment_point/{shipment_point_id}',
    summary='Update shipment point with given ID',
    response_description='Shipment point updated',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def partner_shipment_point_delete(
    shipment_point_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['sp:u'],
    ),
    default_filter_args: list = fastapi.Depends(
        shipment_point_default_filter_args
    ),
) -> fastapi.Response:
    """Update partner shipment point with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: provided partner not found
    """
    actions = ShipmentPointActions()
    await actions.shipment_point_delete(
        shipment_point_id=shipment_point_id,
        default_filter_args=default_filter_args,
    )

    return fastapi.responses.Response(status_code=204)
