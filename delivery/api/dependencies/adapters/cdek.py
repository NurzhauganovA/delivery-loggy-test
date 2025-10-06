from fastapi import Depends

from api.adapters.cdek import CDEKAdapter
from api.dependencies.clients import get_cdek_client

__singleton: CDEKAdapter | None = None


async def get_cdek_adapter(
        client = Depends(get_cdek_client),
) -> CDEKAdapter:
    global __singleton
    if __singleton is None:
        __singleton = CDEKAdapter(
            client=client,
        )

    return __singleton
