import fastapi
from api import schemas, auth
from fastapi_pagination.bases import AbstractPage

from .schemas import (
    PartnerShipmentPointGet, PartnerShipmentPointFilterV2
)
from .dependecies import (
    shipment_point_default_filter_args,
)

from .actions import ShipmentPointActions

router = fastapi.APIRouter()

@router.get(
    '/shipment_point/list',
    summary='Get list of partners shipment points',
    response_model=schemas.Page[schemas.PartnerShipmentPointGet],
    response_description='List of partner shipment_points',
)
async def shipment_point_get_list_v2(
    filter_kwargs: schemas.ShipmentPointFilter = fastapi.Depends(PartnerShipmentPointFilterV2),
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