import asyncio
from datetime import datetime
from typing import List

import aiohttp
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch

from api import exceptions
from api.controllers.handle_order_status_transition.handlers import (
    SendOTPHandler,
    VerifyOTPHandler,
)
from api.controllers.handle_order_status_transition.handlers.send_otp.exceptions import (
    SendOTPPartnerNotFoundError,
    BaseOTPSendError,
)
from api.controllers.handle_order_status_transition.handlers.verify_otp.exceptions import (
    VerifyOTPPartnerNotFoundError,
    BaseOTPVerifyError,
    VerifyOTPWrongCodeError,
)
from api.logging_module import logger
from .external_order_create.get_product_payload import get_product_payload
from .websocket_managers import websocket_manager
from .ws_monitoring import ws_authenticate
from .. import enums
from .. import models
from .. import schemas
from .. import services
from ..common import schema_base
from ..enums import PostControlType
from ..schemas import UserCurrent


async def order_get_list(pagination_params, default_filter_args, filter_params) -> list:
    orders = await models.order_get_list(
        pagination_params,
        default_filter_args=default_filter_args,
        filter_args=filter_params,
    )
    return orders


async def order_get_list_v2(pagination_params, default_filter_args, filter_params, profile_type) -> list:
    orders = await models.order_get_list_v2(
        pagination_params,
        default_filter_args=default_filter_args,
        filter_args=filter_params,
        profile_type=profile_type
    )
    return orders


async def order_get_v2(order_id, default_filter_args, profile_type):
    orders = await models.order_get_v2(
        order_id=order_id,
        default_filter_args=default_filter_args,
        profile_type=profile_type,
    )
    return orders


async def order_get_count(default_filter_args, filter_args) -> dict:
    orders_count = await models.orders_get_count(
        default_filter_args=default_filter_args,
        filter_args=filter_args,
    )

    return {
        'count': orders_count
    }


async def order_statuses_get_count(order_default_args, order_group_default_args, profile_type) -> dict:
    orders_count = await models.order_statuses_get_count(
        order_default_args=order_default_args,
        order_group_default_args=order_group_default_args,
        profile_type=profile_type,
    )
    return orders_count


async def order_get_list_mobile(pagination_params, default_filter_args, filter_args):
    orders = await models.order_get_list_mobile(
        pagination_params,
        default_filter_args=default_filter_args,
        filter_args=filter_args,
    )
    return orders


# Используется только для api/v1/order/{order_id}
async def order_get_v1(order_id: int, default_filter_args, profile_type) -> dict:
    orders = await models.order_get_v1(order_id, default_filter_args, profile_type)
    return orders


async def order_create(
    order: schemas.OrderCreate,
    user: schemas.UserCurrent,
    courier_service_id: int,
):
    try:
        await models.order_create(
            create=order,
            courier_service_id=courier_service_id,
            user=user,
        )

    except (
        models.EntityDoesNotExist,
        models.OrderEntitiesError,
        models.OrderReceiverIINNotProvided,
        models.NotDistributionOrdersError,
        models.NotDistributionCouriersError,
        models.InvalidPointCoords,
        models.PartnerNotFound,
        models.ProfileNotFound,
        models.OrderAlreadyHaveCourierError,
    ) as e:
        raise exceptions.HTTPBadRequestException(e)


async def order_create_v2(
    order: schemas.OrderCreateV2,
    user: schemas.UserCurrent,
    distribute_now: bool,
    courier_service_id: int,
):
    product_payload = get_product_payload(
        product_type=order.product_type,
        payload=order.payload,
    )

    try:
        return await models.order_create_v2(
            create=order,
            product_payload=product_payload,
            courier_service_id=courier_service_id,
            distribute_now=distribute_now,
            user=user,
        )

    except (
        models.EntityDoesNotExist,
        models.OrderEntitiesError,
        models.OrderReceiverIINNotProvided,
        models.NotDistributionOrdersError,
        models.NotDistributionCouriersError,
        models.InvalidPointCoords,
        models.PartnerNotFound,
        models.ProfileNotFound,
        models.OrderAlreadyHaveCourierError,
    ) as e:
        raise exceptions.HTTPBadRequestException(e)


async def order_update(
    order_id: int,
    update: schemas.OrderUpdate,
    default_filter_args,
):
    return await models.order_update(
        order_id=order_id,
        update=update,
        default_filter_args=default_filter_args,
    )


async def order_cancel(
    order_id: int,
    reason: str,
    user: UserCurrent,
    default_filter_args: list,
    comment: str | None = None,
):
    try:
        order_obj = await models.Order.get(*default_filter_args, id=order_id)
    except DoesNotExist:
        raise exceptions.HTTPNotFoundException()

    return await models.order_request_cancellation(
        order_obj=order_obj,
        reason=reason,
        user=user,
        comment=comment,
    )


async def order_accept_cancel(
    order_id: int,
    user: UserCurrent,
    default_filter_args: list,
):
    try:
        order_obj = await models.Order.get(*default_filter_args, id=order_id)

    except DoesNotExist:
        raise exceptions.HTTPNotFoundException()

    return await models.order_accept_cancel(order_obj=order_obj, user=user)


async def order_postpone(order_id: int, until: datetime, comment: str, user: UserCurrent, default_filter_args: list):
    return await models.order_postpone(order_id, until, comment, user, default_filter_args)


async def order_finalize_at_cs(order_id: int, comment: str, user: UserCurrent, default_filter_args: list):
    return await models.order_finalize_at_cs(order_id, comment, user, default_filter_args)


async def order_noncall(order_id: int, comment: str, user: UserCurrent, default_filter_args: list):
    return await models.order_noncall(order_id, comment, user, default_filter_args)


async def order_resume(order_id: int, user: UserCurrent, new_delivery_datetime, default_filter_args: list):
    return await models.order_resume(order_id, user, new_delivery_datetime, default_filter_args)


async def order_courier_assign(default_filter_args, order_id, courier_id, current_user: UserCurrent):
    if courier_id is not None:
        return await models.order_courier_assign(default_filter_args, order_id, courier_id, user=current_user)
    else:
        return await models.order_expel_courier(
            order_id=order_id,
            current_user=current_user,
            default_filter_args=default_filter_args,
        )


async def order_update_status(
    order_id: int,
    status_id: int,
    default_filter_args,
) -> dict:
    try:
        updated_status = await models.order_update_status(order_id, status_id, default_filter_args)
        return updated_status
    except (
        models.OrderEntitiesError,
        models.StatusAlreadyCurrent,
        models.StatusAfterError,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def order_current_status(
    order_id: int,
    default_filter_args,
) -> schemas.OrderStatusGet:
    return await models.order_get_current_status(order_id, default_filter_args=default_filter_args)


async def order_import_history(
    **kwargs
) -> List[schemas.HistoryGet]:
    return await models.order_import_history(**kwargs)


async def order_revise(default_filters: list, order_id: int, revised: bool):
    await models.order_revise(default_filters=default_filters, order_id=order_id, revised=revised)


async def order_sms_postcontrol(
        order_id,
        default_filter_args,
        at_client_point: schemas.Coordinates,
        send_otp_handler: SendOTPHandler,
):
    # Получаем заказ по ID
    try:
        order = await models.Order.filter(*default_filter_args).distinct().get(id=order_id).select_related('city')
    except DoesNotExist:
        raise DoesNotExist(f'Order with given ID: {order_id} was not found')

    # Получим статус send_otp
    try:
        status = await models.Status.get(code='send_otp')
    except DoesNotExist:
        raise DoesNotExist(f'Status with given code: send_otp was not found')

    # Перенаправляем исполнение в send_otp_handler
    try:
        await send_otp_handler.handle(
            order_obj=order,
            status=status,
            data=at_client_point.dict() if at_client_point else None,
        )
        return

    except SendOTPPartnerNotFoundError:
        # Если нет ОТП сервиса у партнера, то игнорируем исключение и вызываем наш сервис
        pass
    except BaseOTPSendError as e:
        raise exceptions.HTTPBadRequestException(e) from e
    except Exception as e:
        logger.bind(order_id=order_id).error(e)
        raise exceptions.HTTPBadRequestException("Unexpected error") from e

    # Наш ОТП сервис
    try:
        await models.order_sms_postcontrol(
            order=order,
            at_client_point=at_client_point,
        )
    except Exception as e:
        logger.bind(order_id=order_id).error(e)
        raise exceptions.HTTPBadRequestException("Unexpected error") from e


async def order_sms_postcontrol_check(
        order_id,
        code,
        default_filter_args,
        code_sent_point,
        verify_otp_handler: VerifyOTPHandler
):
    # Получаем заказ по ID
    try:
        order = await models.Order.filter(
            *default_filter_args,
        ).distinct().get(id=order_id).select_related(
            'deliverygraph', 'city'
        )
    except DoesNotExist:
        raise DoesNotExist(f'Order with given ID: {order_id} was not found')

    # Получим статус verify_otp
    try:
        status = await models.Status.get(code='verify_otp')
    except DoesNotExist:
        raise DoesNotExist(f'Status with given code: send_otp was not found')

    # Перенаправляем исполнение в verify_otp_handler
    try:
        await verify_otp_handler.handle(
            order_obj=order,
            status=status,
            data=dict(
                code=code,
                code_sent_point=code_sent_point.dict() if code_sent_point else None,
            ),
        )
        order = await models.get_order_for_order_sms_postcontrol_check(order_id=order_id)
        return order

    except VerifyOTPPartnerNotFoundError:
        # Если нет ОТП сервиса у партнера, то игнорируем исключение и вызываем наш сервис
        pass
    except VerifyOTPWrongCodeError as e:
        raise exceptions.HTTPBadRequestException(str(enums.OrderSMS.NOT_MATCH)) from e
    except BaseOTPVerifyError as e:
        raise exceptions.HTTPBadRequestException("error during verify OTP") from e
    except Exception as e:
        logger.bind(order_id=order_id).error(e)
        raise exceptions.HTTPBadRequestException("Unexpected error") from e

    # Наш ОТП сервис
    try:
        return await models.order_sms_postcontrol_check(
            order=order,
            code=code,
            code_sent_point=code_sent_point,
        )
    except models.OrderSmsCheckError as e:
        raise exceptions.HTTPBadRequestException(str(e))
    except Exception as e:
        logger.bind(order_id=order_id).error(e)
        raise exceptions.HTTPBadRequestException("Unexpected error") from e


async def order_cancel_at_client(order_id, image, reason, current_user: UserCurrent, default_filter_args):
    return await models.order_cancel_at_client(order_id, image, reason, current_user, default_filter_args)


async def order_reschedule(current_user: UserCurrent, order_id, update):
    if update.place:
        update_address = schemas.OrderAddressChange(
            places=[update.place],
            change_reason=enums.OrderChangeAddressReason.CLIENT_CHANGED,
            comment=update.reason,
            change_type=enums.OrderChangeAddressType.SAVE_COURIER_SAVE_DELIVERY_DATETIME,
            delivery_datetime=update.delivery_datetime
        )
        await order_address_update(current_user, order_id, update_address)
    kwargs = {
        'current_user_id': current_user.id,
        'current_user_role': current_user.profile['profile_type']
    }
    if current_user.profile['profile_type'] == enums.ProfileType.COURIER.value:
        kwargs['courier_id'] = current_user.profile['id']
    return await models.order_reschedule(order_id, update, **kwargs)


async def order_report(query, profile_type, **kwargs):
    try:
        return await models.order_report(query, profile_type, **kwargs)
    except ValueError as e:
        raise exceptions.HTTPBadRequestException(str(e))


async def order_import_from_excel(file, **kwargs) -> schemas.ImportExcelResponse:
    current_user = kwargs.pop('current_user', None)
    try:
        return await models.order_import_from_excel(file, current_user=current_user)
    except (
        models.OrderEntitiesError,
        models.OrderReceiverIINNotProvided,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except (
        services.geocoder.GeocoderRemoteServiceResponseError,
        services.geocoder.GeocoderRemoteServiceRequestError
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e


def order_import_get_sample(current_user: UserCurrent):
    return models.order_import_get_sample(current_user)


async def listen_order_updates(websocket: WebSocket):
    await websocket.accept()
    try:
        current_user = await ws_authenticate(websocket)
        websocket_manager.connect_manager(
            current_user.profile['profile_content']['partner_id'],
            websocket,
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect_manager(websocket)


async def order_biometry_verify(
    order_id: int,
    request_body: schemas.BiometryVerifyBody,
):
    try:
        await models.order_biometry_verify(
            order_id=order_id, request_body=request_body)
    except models.StatusAfterError as e:
        raise exceptions.HTTPBadRequestException(str(e))


async def order_distribution(**kwargs) -> None:
    try:
        await models.order_distribution_for_area(**kwargs)
    except (
        models.NotDistributionOrdersError,
        models.NotDistributionCouriersError,
        models.StatusAlreadyCurrent,
        models.DistanceMatrixError,
        services.geocoder.GeocoderRemoteServiceResponseError,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e))
    except (
        asyncio.TimeoutError,
        aiohttp.ClientConnectorError,
        services.geocoder.GeocoderRemoteServiceRequestError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e


async def order_distribution_selective(**kwargs):
    try:
        return await models.order_distribution_selective(**kwargs)
    except (
        models.NotDistributionOrdersError,
        models.NotDistributionCouriersError,
        models.StatusAlreadyCurrent,
        models.DistanceMatrixError,
        services.geocoder.GeocoderRemoteServiceResponseError,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e))
    except (
        asyncio.TimeoutError,
        aiohttp.ClientConnectorError,
        services.geocoder.GeocoderRemoteServiceRequestError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e


async def order_mass_courier_assign(data: schemas.OrderMassCourierAssign, bg, default_filter_args):
    try:
        await models.order_mass_courier_assign(data, bg, default_filter_args=default_filter_args)
    except (
        models.ProfileNotFound,
    ) as e:
        raise exceptions.HTTPNotFoundException(e)
    except (
        models.StatusAlreadyCurrent,
        models.StatusAfterError,
        models.StatusAlreadySet,
    ) as e:
        raise exceptions.HTTPBadRequestException(e)


async def order_mass_status_update(data: schemas.OrderMassStatusUpdate, **kwargs):
    try:
        return await models.order_mass_status_update(data, **kwargs)
    except models.OrderNotFound as e:
        raise exceptions.HTTPNotFoundException(e)


async def order_restore(
    order_id: int,
    current_user: UserCurrent,
    update: schemas.OrderRestore,
):
    try:
        await models.order_restore(
            order_id=order_id,
            update=update,
            user=current_user,
        )
    except (
        models.OrderAlreadyDelivered,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def order_address_update(
    current_user: UserCurrent,
    order_id: int,
    update: schemas.OrderAddressChange
) -> dict:
    try:
        await models.order_address_update(
            order_id, update,
            current_user,
        )
        return await models.order_get(order_id, profile_type=current_user.profile['profile_type'])
    except (
        models.PlaceNotFound,
        models.EntityDoesNotExist,
        models.NotDistributionCouriersError,
        models.NotDistributionOrdersError,
        models.ProfileNotFound,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def order_address_update_v2(
    current_user: UserCurrent,
    order_id: int,
    update: schemas.OrderAddressChangeV2
):
    try:
        await models.order_address_update_v2(
            order_id, update,
            current_user,
        )
    except (
        models.PlaceNotFound,
        models.EntityDoesNotExist,
        models.NotDistributionCouriersError,
        models.NotDistributionOrdersError,
        models.ProfileNotFound,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def order_current_status_external(
    order_id: int,
    api_key: str,
) -> schemas.OrderStatusGet:
    try:
        token = await models.PublicApiToken.filter(token=api_key).first()
        if not token:
            raise models.PublicApiTokenNotFound('Cannot get partner with provided api key')

        await models.order_get(order_id, [Q(partner_id=token.partner_id)])

        return await models.order_get_current_status(order_id)
    except DoesNotExist as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e
    except models.PublicApiTokenNotFound as e:
        raise exceptions.HTTPUnauthenticatedException(str(e)) from e


async def order_change_status(default_filter_args, body):
    return await models.order_change_status(default_filter_args, body)


async def order_pan(order_id: int, pan_schema: schemas.OrderPAN, default_filter_args):
    try:
        return await models.order_pan(order_id, pan_schema, default_filter_args=default_filter_args)
    except ValueError as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def order_pan_v2(order_id: int, pan_schema: schemas.OrderPAN, default_filter_args):
    try:
        return await models.order_pan_v2(order_id, pan_schema=pan_schema, default_filter_args=default_filter_args)
    except ValueError as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e


async def external_order_cancel(order_id: int, default_filter_args, current_user: UserCurrent):
    delivery_status = schemas.DeliveryStatus(
        status=enums.OrderDeliveryStatus.CANCELLED,
        reason='Отменено сервисом партнера',
        datetime=None,
        comment=None,
    )

    schema = schema_base.partial(schemas.OrderUpdate)(delivery_status=delivery_status)

    await models.order_update(
        order_id=order_id, update=schema, current_user=current_user,
        default_filter_args=default_filter_args)
