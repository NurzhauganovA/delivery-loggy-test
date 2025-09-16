from typing import Protocol, Optional

from api import models


class OrderStatusTransitionHandlerProtocol(Protocol):
    """Интерфейс обработчика перехода не следующий статус"""
    async def handle(
            self,
            order_obj: 'models.Order',
            status: 'models.Status',
            data: Optional[dict] = None,
    ):
        """Обработчик перехода заявки на следующий статус"""
