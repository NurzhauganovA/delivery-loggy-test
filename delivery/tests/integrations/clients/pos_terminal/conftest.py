import pytest_asyncio

from api.clients.pos_terminal import POSTerminalClient


@pytest_asyncio.fixture(scope="session")
async def client():
    client = POSTerminalClient(
        base_url="https://dev-2-all-proxy-in-one.trafficwave.kz/colvir/damu/tms",
        authorization="Basic b3ZlcmRyYWZ0OldmbWhldFprbTZDa21qZm9CY2QzcFRRclZ0dEZzNUhU"
    )

    yield client

    await client.aclose()
