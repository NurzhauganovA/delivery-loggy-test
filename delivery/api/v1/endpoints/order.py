import json
from datetime import datetime
from typing import List, Annotated

import fastapi
import slugify
from fastapi import Security, Depends
from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import constr
from starlette.responses import FileResponse, JSONResponse, StreamingResponse
from starlette.responses import Response
from starlette.websockets import WebSocket
from tortoise.timezone import now

from api import exceptions, models
from api.common import schema_base
from api.controllers.get_order_product import OrderProductNotFoundError
from api.controllers.handle_order_status_transition.handlers import (
    SendOTPHandler,
    VerifyOTPHandler,
)
from api.dependencies.controllers.handle_order_status_transition.handlers import (
    get_send_otp_handler,
    get_verify_otp_handler,
)
from ... import auth
from ... import controllers
from ... import dependencies
from ... import responses
from ... import schemas
from ...enums import ProfileType
from ...modules.order.dependecies import order_group_default_filter_args

router = fastapi.APIRouter()


@router.put(
    '/order/mass-set-status',
    status_code=200,
)
async def order_change_status(
    body: schemas.OrderChangeStatus,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:cs']
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter())
):
    logger.debug(_)
    logger.debug(body)
    await controllers.order_change_status(default_filter_args, body)


@router.post(
    '/order/report',
    summary='Get order report',
)
async def order_report(
    query: schemas.ExportExcel,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:r'],
    ),
):
    profile_type = current_user.profile['profile_type']
    profile_content = current_user.profile['profile_content']
    kwargs = {}
    if profile_type == ProfileType.MANAGER:
        kwargs['partner_id'] = profile_content['partner_id']
    if profile_type == ProfileType.BANK_MANAGER:
        kwargs['partner_id__in'] = current_user.partners
        kwargs['idn__isnull'] = False
    if profile_type == ProfileType.SERVICE_MANAGER:
        kwargs['partner_id__in'] = current_user.partners
    if profile_type == ProfileType.SORTER:
        kwargs['partner_id__in'] = current_user.partners
        kwargs['sorter_id'] = current_user.profile['id']
    if profile_type == ProfileType.SUPERVISOR:
        kwargs['partner_id__in'] = current_user.partners
        kwargs['city__country_id'] = profile_content['country_id']
    if profile_type == ProfileType.LOGIST:
        kwargs['partner_id__in'] = current_user.partners
        kwargs['city__country_id'] = profile_content['country_id']
    kwargs['is_superuser'] = current_user.is_superuser
    report = await controllers.order_report(
        query=query,
        profile_type=profile_type,
        **kwargs,
    )
    current = now()
    filename = 'Report from'
    headers = {
        'Content-Disposition': f'attachment; filename="{filename} {current.date()}.xlsx"'
    }
    return fastapi.responses.StreamingResponse(
        content=report,
        media_type='application/ms-excel',
        headers=headers,
    )


@router.get(
    '/order/list',
    summary='Get list of orders',
    response_model=schemas.Page[schemas.OrderList],
    response_description='List of orders',
)
async def order_get_list(
    filter_args: list = fastapi.Depends(dependencies.order_get_filter_args),
    pagination_params: schemas.Params = fastapi.Depends(schemas.Params),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:l'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    """
    Get a list of orders.

    **ADDITIONAL PARAMS**

    delivery_status:
    * empty list - get all orders
    * null option - get all orders where delivery_status = null

    """
    result = await controllers.order_get_list(
        pagination_params,
        default_filter_args=default_filter_args,
        filter_params=filter_args,
    )
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/order/count',
    summary='Check orders count',
    response_model=schemas.OrdersCount,
    response_description='Count of orders',
)
async def order_get_count(
    filter_args: list = fastapi.Depends(dependencies.order_get_filter_args),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:l'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
) -> dict:
    """
    Get a list of orders.

    **ADDITIONAL PARAMS**

    delivery_status:
    * empty list - get all orders
    * null option - get all orders where delivery_status = null

    """
    return await controllers.order_get_count(
        default_filter_args=default_filter_args,
        filter_args=filter_args,
    )


@router.get(
    '/order/statuses/count',
    summary='Get counts of each status orders',
    response_description='Count of orders',
)
async def order_statuses_get_count(
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:l'],
    ),
    order_default_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
    order_group_default_args: list = fastapi.Depends(
        order_group_default_filter_args
    ),
) -> dict:
    """
    Get a counts of each status orders.
    """
    return await controllers.order_statuses_get_count(
        order_default_args=order_default_args,
        order_group_default_args=order_group_default_args,
        profile_type=user.profile['profile_type'],
    )


@router.get(
    '/order/{order_id}',
    summary='Get order',
    response_model=schemas.OrderGetV1,
    response_description='Order',
)
async def order_get(
    order_id: int,
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:g'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    """Get order with provided ID.

    Returns 404 NOT FOUND due to the following statuses:
    * `not_found`: order not found
    """
    result = await controllers.order_get_v1(
        order_id=order_id,
        default_filter_args=default_filter_args,
        profile_type=user.profile['profile_type'],
    )

    return JSONResponse(jsonable_encoder(result))


@router.post(
    '/order',
    summary='Create order',
    response_model=schemas.OrderGet,
    response_description='Created order',
    status_code=200,
)
async def order_create(
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:c'],
    ),
    order: schemas.OrderCreate = fastapi.Depends(dependencies.order_validate_create_payload),
    courier_service_id: int = fastapi.Depends(dependencies.get_courier_service_id),

):
    """Create order. """
    await controllers.order_create(
        order,
        user=user,
        courier_service_id=courier_service_id,
    )
    return Response(status_code=200)


@router.put(
    '/order/{order_id}',
    summary='Update order',
    response_description='Updated order',
    status_code=200,
)
async def order_update(
    order_id: int,
    update: schemas.OrderUpdate,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    """Update order with provided ID.
    """
    await controllers.order_update(
        order_id,
        update,
        default_filter_args=default_filter_args,
    )
    return Response(status_code=200)


@router.patch(
    '/order/{order_id}',
    summary='Partial update order',
    status_code=200,
)
async def order_partial_update(
    order_id: int,
    update: schema_base.partial(schemas.OrderUpdate),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    """Partial update order with provided ID.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: entity does not exist

    Returns 404 NOT FOUND due to the following:
    * `not_found`: provided order not found
    """
    await controllers.order_update(
        order_id, update,
        default_filter_args=default_filter_args,
    )

    return Response(status_code=200)


@router.put(
    '/order/{order_id}/assign-courier',
    summary='Assign courier to order',
    status_code=200,
)
async def order_courier_assign(
    order_id: int = fastapi.Depends(dependencies.order_check_if_delivered),
    courier_id: int | None = fastapi.Body(embed=True),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    await controllers.order_courier_assign(
        default_filter_args,
        order_id,
        courier_id,
        current_user,
    )


@router.put(
    '/order/{order_id}/cancel',
    summary='Cancel',
    status_code=200,
)
async def order_cancel(
    order_id: int = fastapi.Depends(dependencies.order_check_for_cancel),
    reason: str = fastapi.Body(embed=True),
    comment: str | None = fastapi.Body(embed=True, default=None),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    await controllers.order_cancel(
        order_id=order_id,
        reason=reason,
        user=user,
        default_filter_args=default_filter_args,
        comment=comment,
    )


@router.put(
    '/order/{order_id}/accept-cancel',
    summary='Cancel',
    status_code=200,
)
async def order_accept_cancel(
    order_id: int = fastapi.Depends(dependencies.order_check_for_accept_cancel),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    await controllers.order_accept_cancel(
        order_id=order_id,
        user=user,
        default_filter_args=default_filter_args,
    )


@router.put(
    '/order/{order_id}/postpone',
    summary='Postpone',
    status_code=200,
)
async def order_postpone(
    order_id: int = fastapi.Depends(dependencies.order_check_if_delivered),
    until: datetime = fastapi.Body(embed=True),
    comment: str | None = fastapi.Body(None, embed=True),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    await controllers.order_postpone(
        order_id, until=until,
        comment=comment, user=user,
        default_filter_args=default_filter_args,
    )


@router.put(
    '/order/{order_id}/finalize-at-cs',
    summary='Finalize order at courier service',
    status_code=200,
)
async def order_finalize_at_cs(
    order_id: int,
    comment: str | None = fastapi.Body(None, embed=True),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    await controllers.order_finalize_at_cs(
        order_id,
        comment=comment,
        user=user,
        default_filter_args=default_filter_args,
    )


@router.put(
    '/order/{order_id}/noncall',
    summary='Noncall',
    status_code=200,
)
async def order_noncall(
    order_id: int = fastapi.Depends(dependencies.order_check_if_delivered),
    comment: constr(min_length=10, max_length=1000) = fastapi.Body(embed=True),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    await controllers.order_noncall(order_id, comment, user, default_filter_args=default_filter_args)


@router.put(
    '/order/{order_id}/resume',
    summary='Order Resume',
    status_code=200,
)
async def order_resume(
    order_id: int = fastapi.Depends(dependencies.order_check_for_resume),
    new_delivery_datetime: datetime | None = fastapi.Depends(
        dependencies.validate_delivery_datetime_for_order_resume,
    ),
    user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    await controllers.order_resume(order_id, user, new_delivery_datetime, default_filter_args=default_filter_args)


@router.put(
    '/order/{order_id}/cancel-at-client',
    summary='Cancel order at client',
    status_code=200,
)
async def order_cancel_at_client(
    order_id: int,
    reason: str = fastapi.Body(),
    image: fastapi.UploadFile = fastapi.Depends(dependencies.order_validate_image_for_cancel_at_client),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:cc'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    await controllers.order_cancel_at_client(
        order_id=order_id,
        image=image,
        reason=reason,
        current_user=current_user,
        default_filter_args=default_filter_args,
    )


@router.put(
    '/order/{order_id}/reschedule',
    summary='Reschedule order',
    status_code=200,
)
async def order_reschedule(
    order_id: int,
    update: schemas.OrderReschedule,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:cc'],
    )
):
    await controllers.order_reschedule(current_user, order_id, update)


@router.patch(
    '/order/{order_id}/restore',
    summary='Restore order patch',
    status_code=200,
    response_description='Restore order',
)
async def order_restore(
    order_id: int,
    update: schema_base.partial(schemas.OrderRestore),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
):
    """Restore order with provided ID.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: entity does not exist

    Returns 404 NOT FOUND due to the following:
    * `not_found`: provided order not found
    """
    await controllers.order_restore(
        order_id, current_user, update,
    )

    return Response(status_code=200)


@router.get(
    '/order/{order_id}/status',
    summary='Get order current status',
    response_model=schemas.OrderStatusGet,
    response_description='Order current status',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def order_get_current_status(
    order_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:g']
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter(prefix='order__')),
) -> schemas.OrderStatusGet:
    """Returns order current status with provided ID.

    Returns 404 NOT FOUND due to the following:
    * `not_found`: provided order not found
    """
    return await controllers.order_current_status(
        order_id,
        default_filter_args=default_filter_args,
    )


@router.get(
    '/order/import/history',
    summary='Get history of ImportOrder',
    response_model=List[schemas.HistoryGet],
    response_description='Import history of order',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def order_get_import_history(
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:g']
    ),
) -> List[schemas.HistoryGet]:
    return await controllers.order_import_history(current_user=current_user)


@router.put(
    '/order/{order_id}/status',
    summary='Update order status',
    response_description='Updated order',
    response_model=schemas.OrderStatusGet,
)
async def order_update_status(
    order_id: int,
    status_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
    _validated_payload: bool = fastapi.Depends(dependencies.order_status_validate_payload),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
) -> dict:
    """Update order status with provided ID.

    Returns 404 NOT FOUND due to the following:
    * `not_found`: provided order not found
    """
    return await controllers.order_update_status(
        order_id=order_id,
        status_id=status_id,
        default_filter_args=default_filter_args,
    )


@router.patch(
    '/order/{order_id}/revise',
    summary='Mark order as revised or opposite',
    status_code=200,
)
async def order_revise(
    order_id: int,
    revised: Annotated[bool, fastapi.Body(embed=True)],
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
    default_filter_args: list = fastapi.Security(dependencies.order_revise_default_filters),
):
    await controllers.order_revise(
        default_filters=default_filter_args,
        order_id=order_id,
        revised=revised,
    )


# Disable due to security reason. Can be enabled when security has been established.
# @router.post(
#     '/order/{order_id}/postcontrol-biometry-success',
#     summary='Callback function for biometry service to confirm that post-control passed',
#     response_description='Order delivery status set to video_verification_passed',
#     status_code=204,
# )
# async def order_postcontrol_biometry_success(
#     order_id: int,
#     request_body: schemas.BiometryVerifyBody,
# ) -> Response:
#     await controllers.order_biometry_verify(order_id=order_id, request_body=request_body)
#     return Response(status_code=204)


@router.get(
    '/order/list/my/mobile',
    summary='Get list of orders for mobile app',
    response_model=schemas.Page[schemas.OrderListMobile],
    response_description='List of orders',
)
async def order_get_list_my_mobile(
    pagination_params: schemas.Params = fastapi.Depends(schemas.Params),
    filter_args: list = fastapi.Depends(dependencies.order_get_filter_args),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:l'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
):
    result = await controllers.order_get_list_mobile(
        pagination_params=pagination_params,
        default_filter_args=default_filter_args,
        filter_args=filter_args,
    )
    return JSONResponse(jsonable_encoder(result))


@router.options(
    '/order/import/sample',
    summary='Get sample excel for import',
    response_description='Sample excel list for import',
)
def order_import_get_sample(
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:c'],
    )
) -> FileResponse:
    """Get sample excel for import."""
    return FileResponse(
        path=controllers.order_import_get_sample(current_user),
        media_type='application/octet-stream',
        filename='orders_sample.xlsx',
    )


@router.post(
    '/order/import',
    summary='Import orders from excel',
    response_description='Orders imported successfully',
)
async def order_import_from_excel(
    excel: fastapi.UploadFile = fastapi.File(...),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:c']
    )
) -> StreamingResponse:
    result = await controllers.order_import_from_excel(excel, current_user=current_user)

    filename = f"{slugify.slugify(excel.filename.split('.', 2)[0])}.xlsx"

    response = StreamingResponse(
        content=result.file,
        media_type='application/octet-stream',
        headers={
            'X-Result': result.result,
            'Content-Disposition': f'attachment; filename={filename}'
        },
    )
    return response


@router.post(
    '/order/{order_id}/sms-postcontrol',
    summary='Send sms to receiver',
)
async def sms_postcontrol(
    order_id: int,
    at_client_point: schemas.Coordinates | None = fastapi.Body(None),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
    send_otp_handler: SendOTPHandler = Depends(get_send_otp_handler)
):
    await controllers.order_sms_postcontrol(
        order_id=order_id,
        default_filter_args=default_filter_args,
        at_client_point=at_client_point,
        send_otp_handler=send_otp_handler,
    )


@router.post(
    '/order/{order_id}/sms-postcontrol/check',
    summary='Order sms postcontrol check',
    response_model=schemas.OrderGetV1,
)
async def sms_postcontrol_check(
    order_id: int,
    body: schemas.OrderSmsCode,
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
    verify_otp_handler: VerifyOTPHandler = Depends(get_verify_otp_handler)
):
    return await controllers.order_sms_postcontrol_check(
        order_id=order_id,
        code=body.code,
        default_filter_args=default_filter_args,
        code_sent_point=body.code_sent_point,
        verify_otp_handler=verify_otp_handler,
    )


@router.websocket('/listen-order-updates')
async def listen_order_updates(websocket: WebSocket):
    await controllers.listen_order_updates(websocket)


@router.post(
    '/order/distribution',
    summary='Distribution of orders between couriers',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseNoContent,
        ],
    ),
    status_code=204,
)
async def distribution(
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
) -> fastapi.Response:
    """Distribution of orders between couriers."""
    await controllers.order_distribution(current_user=current_user)
    return fastapi.Response(status_code=204)


@router.post(
    '/order/mass-courier-assign',
    summary='Assign courier to mass orders',
    status_code=200,
)
async def order_mass_courier_assign(
    data: schemas.OrderMassCourierAssign,
    bg: fastapi.BackgroundTasks,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter())
):
    await controllers.order_mass_courier_assign(data, bg, default_filter_args=default_filter_args)


@router.post(
    '/order/mass-status-update',
    summary='Assign courier to mass orders',
    status_code=200,
)
async def order_mass_status_update(
    data: schemas.OrderMassStatusUpdate,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:u'],
    ),
):
    kwargs = {'partner_id__in': current_user.partners,
              'current_user': current_user}
    await controllers.order_mass_status_update(data, **kwargs)


@router.post(
    '/order/distribution/selective',
    summary='Distribution selective orders between couriers',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
        ],
    ),
    status_code=204,
)
async def distribution_selective_orders(
    selective_order_ids: List[int],
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['o:dist'],),
) -> fastapi.Response:
    """Distribution of orders between couriers."""
    response = await controllers.order_distribution_selective(
        current_user=current_user, selective_order_ids=selective_order_ids
    )
    return fastapi.Response(status_code=200, content=json.dumps(
        {
            "not_distributed_orders": response
        }
    ))


@router.patch(
    '/order/address/{order_id}',
    summary='Update order',
    response_model=schemas.OrderGet,
    response_description='Order address updated order',
    responses=responses.generate_responses(
        [
            responses.APIResponseNotFound,
            responses.APIResponseBadRequest,
        ],
    ),
)
async def order_address_update(
    order_id: int,
    update: schemas.OrderAddressChange,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
):
    """Update order with provided ID.

    Returns 400 BAD REQUEST due to the following statuses:
    * `bad_request`: entity does not exist

    Returns 404 NOT FOUND due to the following:
    * `not_found`: provided order not found
    """
    await controllers.order_address_update(
        current_user=current_user,
        order_id=order_id,
        update=update,
    )
    return fastapi.responses.Response(status_code=204)


@router.post(
    '/order/{order_id}/pan',
    summary='Transfer pan of cards to external API',
    response_description='Order PAN',
    response_model=schemas.OrderGetV1
)
async def order_pan(
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
    result = await controllers.order_pan(
        order_id=order_id,
        pan_schema=pan,
        default_filter_args=default_filter_args,
    )
    logger.debug(jsonable_encoder(result))
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/order/{order_id}/product/{product_id}',
    summary='Get order product',
    response_model=schemas.Product,
    responses=responses.make_error_responses(include=[400, 401, 403, 404, 500])
)
async def get_order_product(
    order_id: int,
    product_id: int,
    default_filter_args: list = fastapi.Security(dependencies.OrderDefaultFilter()),
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['op:g'],
    ),
):
    """Получение продукта у заявки"""
    try:
        product = await controllers.get_order_product(
            order_id=order_id,
            product_id=product_id,
            default_filter_args=default_filter_args,
        )
        return product

    except OrderProductNotFoundError as e:
        raise exceptions.HTTPNotFoundException(e)
    except Exception as e:
        raise exceptions.HTTPBadRequestException(e)
