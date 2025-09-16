import fastapi
from starlette.responses import Response

from api import schemas, auth

from .dependecies import *
from .actions import *
from .schemas import *

router = fastapi.APIRouter()


@router.post(
    '/delivery_point',
    summary='Create delivery point and return created object',
    response_description='delivery point created',
    response_model=DeliveryPointGet,
    status_code=201,
)
async def delivery_point_create(
    delivery_point: DeliveryPointCreate = fastapi.Depends(
        delivery_point_validate_payload
    ),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['sp:c'],
    ),
):
    """
    Create delivery point with given payload.
    """
    actions = DeliveryPointActions()
    result = await actions.delivery_point_create(
        delivery_point=delivery_point
    )

    return result


@router.patch(
    '/delivery_point/{delivery_point_id}',
    summary='Update delivery point with given ID',
    response_description='delivery point updated',
    response_model=DeliveryPointGet,
    status_code=200,
)
async def delivery_point_partial_update(
    delivery_point_id: int,
    update: DeliveryPointUpdate = fastapi.Depends(
        delivery_point_validate_payload
    ),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['sp:u'],
    ),
    default_filter_args: list = fastapi.Depends(
        delivery_point_default_filter_args
    ),
):
    """Update partner delivery point with provided ID and return updated object.
    """
    actions = DeliveryPointActions()
    result = await actions.delivery_point_update(
        delivery_point_id=delivery_point_id,
        update=update,
        default_filter_args=default_filter_args,
    )

    return result


@router.delete(
    '/delivery_point/{delivery_point_id}',
    summary='Update delivery point with given ID and return updated object',
    response_description='delivery point updated',
    status_code=204,
)
async def delivery_point_delete(
    delivery_point_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['sp:u'],
    ),
    default_filter_args: list = fastapi.Depends(
        delivery_point_default_filter_args
    ),
) -> Response:
    """
    Update delivery point with provided ID.
    """
    actions = DeliveryPointActions()
    await actions.delivery_point_delete(
        delivery_point_id=delivery_point_id,
        default_filter_args=default_filter_args,
    )

    return Response(status_code=204)
