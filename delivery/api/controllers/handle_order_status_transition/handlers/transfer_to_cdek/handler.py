from typing import Optional

from pydantic import ValidationError

from api import models

from api.controllers.handle_order_status_transition.handler_protocol import(
    OrderStatusTransitionHandlerProtocol,
)

from api.dependencies.clients.cdek import get_cdek_client
from api.adapters.cdek import CDEKAdapter

from .exceptions import(
    CDEKValidationError,
)
from .schema import(
    CDEKOrder,
)
from api.enums import(
    StatusSlug,
    OrderDeliveryStatus,
    CourierService,
    CourerServiceType,
)


class TransferToCDEK(OrderStatusTransitionHandlerProtocol):

    delivery_status = {
        'status': OrderDeliveryStatus.TRANSFER_TO_CDEK.value,
        'datetime': None,
        'reason': None,
        'comment': None,
    }

    def __init__(self, cdek_adapter: CDEKAdapter):
        self.__cdek_adapter = cdek_adapter

    async def handle(
        self,
        order_obj: 'models.Order',
        status: 'models.Status',
        data: Optional[dict] = None,
    ):
        """Обработчик перехода заявки в transfer_to_cdek"""

        try:
            CDEKOrder(**data)
        except ValidationError as e:
            raise CDEKValidationError('invalid body for CDEK order') from e

        warehouse_id = data['warehouse_id']

        track_number = await self.__cdek_adapter.order_create(
            shipment_point=warehouse_id,
            recipient_name=order_obj.receiver_name,
            recipient_phone=order_obj.receiver_phone_number,
            latitude=data['latitude'],
            longitude=data['longitude'],
            address=data['address'],
            package_number=order_obj.id,
        )

        order_obj.track_number = str(track_number)
        order_obj.delivery_status = self.delivery_status
        order_obj.courier_service = CourierService.CDEK.value
        order_obj.current_status_id = status.id
        await order_obj.save()
