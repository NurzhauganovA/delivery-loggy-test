from fastapi import Depends

from api import(
    schemas,
    models,
    exceptions,
)
from .check_duplicate_order import check_duplicate_partner_order
from .get_partner_id import get_partner_id
from .get_product_payload import get_product_payload
from .exceptions import ExternalOrderCreateDuplicateError

from api.enums import (
    CourerServiceType,
    OrderStatusCodes,
)
from api.controllers.handle_order_status_transition import OrderStatusTransitionHandlers


async def __external_transfer_to_cdek(
    handler: OrderStatusTransitionHandlers,
    order_id: int,
    courier_service: 'models.CourierService',
    order_schema: schemas.ExternalOrderCreate,
) -> None:
    """
    Обновление заявки с передачей в CDEK через хендлеры

    Args:
        order_id: идентификатор записи заказа
        courier_service_type: объект типа курьерской службы
        order_schema: объект с данными из запроса

    Returns:
        None
    """

    status = await models.Status.get(
        slug=OrderStatusCodes.TRANSFER_TO_CDEK.value,
    ).values('id')
    item = await models.Item.get(
        item_identification_code=OrderStatusCodes.TRANSFER_TO_CDEK.value,
    ).values('id')
    order_obj = await models.Order.get(id=order_id)
    order_obj.item_id = item.get('id')
    await order_obj.save()
    data = {
        'warehouse_id': courier_service.warehouse_id,
        'latitude': order_schema.latitude,
        'longitude': order_schema.longitude,
        'address': order_schema.address,
    }

    await handler.transition_order_status(
        order_id=order_id,
        status_id=status.get('id'),
        default_filter_args=[],
        user_id=order_obj.partner_id,
        user_profile=None,
        data=data,
    )


async def external_order_create(
    order: schemas.ExternalOrderCreate,
    api_key: str,
    handler: OrderStatusTransitionHandlers,
) -> int:
    try:
        partner_id = await get_partner_id(api_key)

        # Пока что проверяем дубли по комбинации partner_order_id и partner_id
        if order.partner_order_id:
            await check_duplicate_partner_order(
                partner_order_id=order.partner_order_id,
                partner_id=partner_id,
            )

        product_payload = get_product_payload(
            product_type=order.product_type,
            payload=order.payload,
        )

        order_id = await models.external_order_create_v2(
            order=order,
            product_payload=product_payload,
            partner_id=partner_id,
        )

        courier_service = await models.CourierService.get_or_none(
            partner__id=partner_id,
            city__name_ru=order.city
        ).prefetch_related('city', 'partner')
        courier_cdek_type = CourerServiceType.CDEK.value

        if courier_service and courier_service.courier_service == courier_cdek_type:
            await __external_transfer_to_cdek(
                handler,
                order_id=order_id,
                courier_service=courier_service,
                order_schema=order,
            )

        return order_id

    except (
        models.EntityDoesNotExist,
        models.OrderEntitiesError,
        models.OrderReceiverIINNotProvided,
        models.NotDistributionOrdersError,
        models.InvalidPointCoords,
        models.PartnerNotFound,
        models.ProfileNotFound,
        models.OrderAlreadyHaveCourierError,
        models.OrderAddressNotFound,
        models.ItemNotFound,
        ExternalOrderCreateDuplicateError,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e

    except models.PublicApiTokenNotFound as e:
        raise exceptions.HTTPUnauthenticatedException(str(e)) from e


# TODO: Потом при необходимости вынести в самостоятельный контроллер
async def get_external_order(order_id: int) -> schemas.OrderGetV1:
    try:
        order = await models.get_external_order(
            order_id=order_id,
        )

        return order

    except (
        models.EntityDoesNotExist,
        models.OrderEntitiesError,
        models.OrderReceiverIINNotProvided,
        models.NotDistributionOrdersError,
        models.InvalidPointCoords,
        models.PartnerNotFound,
        models.ProfileNotFound,
        models.OrderAlreadyHaveCourierError,
        models.OrderAddressNotFound,
        models.ItemNotFound,
        ExternalOrderCreateDuplicateError,
    ) as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
