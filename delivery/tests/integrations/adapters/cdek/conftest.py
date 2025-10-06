import pytest

from api.clients.cdek import CDEKClient
from api.adapters.cdek import CDEKAdapter


@pytest.fixture
async def client():
    client = CDEKClient(
        base_url="https://api.cdek.ru/v2",
        client_id="wj9yCGKMfEDQMzMmtzBsiccJOYojcLjn",
        client_secret="cTcEw5CNnmILMeZMAYmShJmIcETlIS0y",
    )

    yield client

    await client.aclose()


@pytest.fixture
async def adapter(client: CDEKClient):
    adapter = CDEKAdapter(
        client=client,
    )

    yield adapter
