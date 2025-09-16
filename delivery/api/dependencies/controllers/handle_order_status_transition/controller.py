from fastapi import Depends

from api.controllers.handle_order_status_transition import (
    OrderStatusTransitionController,
    OrderStatusTransitionHandlers,
)
from .get_handlers import get_handlers

__singleton: OrderStatusTransitionController | None = None


def get_handle_order_status_transition_controller(
        handlers: OrderStatusTransitionHandlers = Depends(get_handlers),
) -> OrderStatusTransitionController:
    global __singleton
    if __singleton is None:
        __singleton = OrderStatusTransitionController(
        handlers=handlers,
    )

    return __singleton
