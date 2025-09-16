from fastapi import Depends

from api.adapters.pos_terminal import POSTerminalAdapter
from api.adapters.pos_terminal.protocols import POSTerminalClientProtocol
from api.dependencies.clients import get_pos_terminal_client

__singleton: POSTerminalClientProtocol | None = None


def get_pos_terminal_adapter(
        client: POSTerminalClientProtocol = Depends(get_pos_terminal_client),
) -> POSTerminalAdapter:
    global __singleton
    if __singleton is None:
        __singleton = POSTerminalAdapter(
            client=client,
        )

    return __singleton
