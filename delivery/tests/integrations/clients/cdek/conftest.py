import pytest_asyncio

from api.clients.cdek import CDEKClient


@pytest_asyncio.fixture(scope="session")
async def client():
    client = CDEKClient(
        base_url="https://api.cdek.ru/v2",
        client_id="wj9yCGKMfEDQMzMmtzBsiccJOYojcLjn",
        client_secret="cTcEw5CNnmILMeZMAYmShJmIcETlIS0y",
    )

    yield client

    await client.aclose()
