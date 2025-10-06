from api import models
from api.schemas.webhooks.cdek import OrderStatusRequest


async def handle_order_status(request: OrderStatusRequest) -> None:
    """
        Метод обработчик статуса заявки CDEK

        Args:
            request: тело запроса, отправляемое нам CDEK-ом

        Returns:
            None
    """
    # Получаем заявку по track number
    order = await models.Order.get(track_number=request.uuid)

    # Сохраняем полученный статус
    await models.CourierServiceStatus.create(
        order_id=order.id,
        status=request.attributes.code,
    )
