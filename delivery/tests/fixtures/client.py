import pytest_asyncio
from httpx import AsyncClient

from api import app
from api.dependencies import partners_ids


@pytest_asyncio.fixture
async def client():

    # Перезапишем для всех тестов partner_id
    app.dependency_overrides[partners_ids.get_freedom_bank_partner_id] = lambda: 1
    app.dependency_overrides[partners_ids.get_pos_terminal_partner_id] = lambda: 2

    async with AsyncClient(app=app, base_url='http://testserver/api') as client:
        yield client
