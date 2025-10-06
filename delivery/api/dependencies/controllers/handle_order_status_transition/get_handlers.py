from fastapi.params import Depends

from api.controllers.handle_order_status_transition import OrderStatusTransitionHandlers
from api.controllers.handle_order_status_transition.handler_protocol import OrderStatusTransitionHandlerProtocol
from api.enums import OrderStatusCodes
from .handlers import (
    get_new_handler,
    get_card_returned_to_bank_handler,
    get_pos_terminal_registration_handler,
    get_transfer_to_cdek_handler,
)

__singleton: OrderStatusTransitionHandlers | None = None


def get_handlers(
        new_handler: OrderStatusTransitionHandlerProtocol = Depends(get_new_handler),
        card_returned_to_bank_handler: OrderStatusTransitionHandlerProtocol = Depends(get_card_returned_to_bank_handler),
        pos_terminal_registration_handler: OrderStatusTransitionHandlerProtocol = Depends(get_pos_terminal_registration_handler),
        transfer_to_cdek: OrderStatusTransitionHandlerProtocol = Depends(get_transfer_to_cdek_handler)
) -> OrderStatusTransitionHandlers:
    global __singleton
    if __singleton is None:
        __singleton = {
            OrderStatusCodes.NEW: new_handler,
            OrderStatusCodes.CARD_RETURNED_TO_BANK: card_returned_to_bank_handler,
            OrderStatusCodes.POS_TERMINAL_REGISTRATION: pos_terminal_registration_handler,
            OrderStatusCodes.TRANSFER_TO_CDEK: transfer_to_cdek,
        }

    return __singleton
