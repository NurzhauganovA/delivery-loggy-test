from typing import Optional

from api import models
from api.controllers.handle_order_status_transition.handler_protocol import OrderStatusTransitionHandlerProtocol


class CardReturnedToBankHandler(OrderStatusTransitionHandlerProtocol):
    async def handle(
        self,
        order_obj: 'models.Order',
        status: 'models.Status',
        data: Optional[dict] = None,
    ):
        """Обработчик перевода заявки в статус card_returned_to_bank"""

        # TODO отказаться от delivery_status, должен быть только один статус у заявки
        delivery_status = {
            'status': None,
            'datetime': None,
            'reason': None,
            'comment': None,
        }
        order_obj.delivery_status = delivery_status
        order_obj.current_status_id = status.id
        await order_obj.save()
