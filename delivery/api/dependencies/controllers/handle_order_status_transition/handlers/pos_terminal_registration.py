from fastapi import Depends

from api.controllers.handle_order_status_transition.handlers import POSTerminalRegistrationHandler
from api.controllers.handle_order_status_transition.handlers.pos_terminal_registration.protocols import POSTerminalAdapterProtocol
from api.dependencies.adapters.pos_terminal import get_pos_terminal_adapter

__singleton: POSTerminalRegistrationHandler | None = None


def get_pos_terminal_registration_handler(
        adapter: POSTerminalAdapterProtocol = Depends(get_pos_terminal_adapter),
) -> POSTerminalRegistrationHandler:
    global __singleton
    if __singleton is None:
        __singleton = POSTerminalRegistrationHandler(
        adapter=adapter,
    )

    return __singleton

