from fastapi import Depends

from api.controllers.handle_order_status_transition.handlers import TransferToCDEK

from api.dependencies.adapters.cdek import get_cdek_adapter
from api.adapters.cdek.adapter import CDEKAdapter

__singleton: TransferToCDEK | None = None


def get_transfer_to_cdek_handler(
    adapter: CDEKAdapter = Depends(get_cdek_adapter)
) -> TransferToCDEK:

    global __singleton
    if __singleton is None:
        __singleton = TransferToCDEK(adapter)

    return __singleton
