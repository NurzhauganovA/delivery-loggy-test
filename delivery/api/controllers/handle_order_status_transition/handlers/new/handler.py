from typing import Optional

from api import models
from api.controllers.handle_order_status_transition.handler_protocol import OrderStatusTransitionHandlerProtocol


class NewHandler(OrderStatusTransitionHandlerProtocol):
    async def handle(
            self,
            order_obj: 'models.Order',
            status: 'models.Status',
            data: Optional[dict] = None,
    ):
        """Обработчик перевода заявки в статус new"""
        # TODO отказаться от delivery_status, должен быть только один статус у заявки
        delivery_status = {
            'status': None,
            'datetime': None,
            'reason': None,
            'comment': None,
        }

        order_obj.delivery_status = delivery_status

        await models.OrderStatuses.filter(order_id=order_obj.id).delete()

        order_time = await order_obj.localtime
        await models.OrderStatuses.create(order=order_obj, status=status, created_at=order_time)
        order_obj.current_status = status
        await models.SMSPostControl.filter(order_id=order_obj.id).delete()
        await order_obj.save()
