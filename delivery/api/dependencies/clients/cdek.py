from api.clients.cdek import CDEKClient
from api.conf import conf

__cdek_client: CDEKClient | None = None


async def get_cdek_client() -> CDEKClient:
    global __cdek_client
    if __cdek_client is None:
        __cdek_client = CDEKClient(
            base_url=conf.cdek.base_url,
            client_id=conf.cdek.client_id,
            client_secret=conf.cdek.client_secret,
        )

    return __cdek_client


async def aclose() -> None:
    if __cdek_client is not None:
        await __cdek_client.aclose()
