from typing import Optional

import fastapi
from fastapi import APIRouter, Depends, Body
from fastapi import Security
from fastapi.encoders import jsonable_encoder
from starlette.responses import Response, JSONResponse
from loguru import logger
from tortoise.exceptions import DoesNotExist

from ...auth import get_current_user
from api import controllers, schemas, dependencies, auth, PydanticException, exceptions
from api.domain.order import DeliveryGraphValidationError, BaseOrderDomainError
from api.dependencies.controllers import get_handle_order_status_transition_controller
from api.controllers.handle_order_status_transition import OrderStatusTransitionController

from api.controllers.update_order_delivery_point.controller import UpdateOrderDeliveryPoint
from api.controllers.update_order_delivery_point.exceptions import(
    BaseUpdateOrderDeliveryPointError,
)

from ...schemas import OrderCreateV2
from ...schemas import UserCurrent
from api.controllers.handle_order_status_transition.exceptions import BaseOrderStatusTransitionHandlerError


router = APIRouter()


@router.post(
    '/order',
    summary='Create order',
    response_description='Created order',
    status_code=201,
)
async def order_create_v2(
    user: schemas.UserCurrent = Security(
        get_current_user,
        scopes=['o:c'],
    ),
    order: schemas.OrderCreateV2 = Depends(dependencies.order_validate_create_payload_v2),
    distribute_now: bool = Body(embed=True),
    courier_service_id: int = Depends(dependencies.get_courier_service_id),

):
    """Create order. """
    # TODO: handle it beautifully
    if distribute_now and not order.delivery_point:
        raise PydanticException(errors=('distribute_now', 'Can not distribute pickup orders'))
    created_order_id = await controllers.order_create_v2(
        order,
        user=user,
        distribute_now=distribute_now,
        courier_service_id=courier_service_id,
    )
    return JSONResponse({'id': created_order_id}, status_code=201)


@router.get(
    '/order/list',
    summary='Get list of orders',
    response_model=schemas.Page[schemas.OrderListV2],
    response_description='List of orders',
)
async def order_get_list_v2(
    filter_args: list = fastapi.Depends(dependencies.order_get_filter_args_v2),
    pagination_params: schemas.Params = fastapi.Depends(schemas.Params),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:l'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilterV2()),
):
    result = await controllers.order_get_list_v2(
        pagination_params,
        default_filter_args=default_filter_args,
        filter_params=filter_args,
        profile_type=user.profile['profile_type'],
    )
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/order/{order_id}',
    summary='Get Order',
    response_model=schemas.OrderGetV2,
    response_description='Get order',
)
async def order_get_v2(
    order_id: int,
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:l'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilterV2()),
):
    result = await controllers.order_get_v2(
        order_id=order_id,
        default_filter_args=default_filter_args,
        profile_type=user.profile['profile_type'],
    )
    return JSONResponse(jsonable_encoder(result))


@router.patch(
    '/order/address/{order_id}',
    summary='Update order',
    response_model=schemas.OrderGet,
    response_description='Order address updated order',
)
async def order_address_update_v2(
    order_id: int,
    update: schemas.OrderAddressChangeV2,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
):
    await controllers.order_address_update_v2(
        current_user=current_user,
        order_id=order_id,
        update=update,
    )
    return fastapi.responses.Response(status_code=204)


@router.post(
    '/order/{order_id}/pan',
    summary='Transfer pan of cards to external API',
    response_description='Order PAN',
    response_model=schemas.OrderGetV2,
)
async def order_pan_v2(
    order_id: int,
    pan: schemas.OrderPAN = fastapi.Depends(dependencies.order_validate_pan),
    _: schemas.UserCurrent = Security(
        auth.get_current_user,
        scopes=['o:p'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    """
    Binds pan of the card to the receiver of the order.
    Then reports respective partner about it.
    """
    result = await controllers.order_pan_v2(
        order_id=order_id,
        pan_schema=pan,
        default_filter_args=default_filter_args,
    )
    logger.debug(jsonable_encoder(result))
    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/order/{order_id}/status',
    summary='Transition order to next status',
)
async def transition_order_status(
    order_id: int,
    status_id: int,
    body: Optional[dict] = Body(default=dict()),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
    controller: OrderStatusTransitionController = Depends(get_handle_order_status_transition_controller),
) -> fastapi.responses.Response:
    """Transition order to next status with provided status_id"""

    try:
        await controller.transition_order_status(
            order_id=order_id,
            status_id=status_id,
            default_filter_args=default_filter_args,
            user_id=current_user.id,
            user_profile=current_user.profile['profile_type'],
            data=body.get('payload'),
        )

        return fastapi.responses.Response(status_code=200)

    except BaseOrderStatusTransitionHandlerError as e:
        raise exceptions.HTTPBadRequestException(e) from e

    except DeliveryGraphValidationError as e:
        raise exceptions.HTTPBadRequestException("support only new version of delivery graph") from e

    except BaseOrderDomainError as e:
        raise exceptions.HTTPBadRequestException(e) from e

    except DoesNotExist as e:
        raise exceptions.HTTPBadRequestException(e) from e


@router.patch(
    '/order/{order_id}/delivery_point',
    summary='Update delivery point',
    description='Update delivery point from courier or supervisor',
)
async def update_delivery_point(
    order_id: int,
    body: schemas.OrderUpdateDeliveryPoint,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
    controller: UpdateOrderDeliveryPoint = Depends(),
) -> fastapi.responses.Response:

    try:
        await controller.init(
            user_id=current_user.id,
            order_id=order_id,
            user_role=current_user.profile['profile_type'],
            data=body.dict(),
            default_filter_args=default_filter_args,
        )
        return fastapi.responses.Response(status_code=200)

    except BaseUpdateOrderDeliveryPointError as e:
        raise exceptions.HTTPBadRequestException(e) from e

    except BaseOrderDomainError as e:
        raise exceptions.HTTPBadRequestException(e) from e

    except DoesNotExist as e:
        raise exceptions.HTTPBadRequestException(e) from e
