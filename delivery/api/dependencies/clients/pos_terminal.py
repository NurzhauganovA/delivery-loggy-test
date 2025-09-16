from api.clients.pos_terminal import POSTerminalClient
from api.conf import conf


__singleton: POSTerminalClient | None = None


def get_pos_terminal_client() -> POSTerminalClient:
    global __singleton
    if __singleton is None:
        __singleton = POSTerminalClient(
        base_url=conf.freedom_pos_terminal_registration.base_url,
        authorization=conf.freedom_pos_terminal_registration.token
    )

    return __singleton


async def aclose_pos_terminal_client() -> None:
    if __singleton is not None:
        await __singleton.aclose()
