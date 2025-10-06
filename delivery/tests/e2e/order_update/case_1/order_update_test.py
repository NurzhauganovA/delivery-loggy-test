from unittest.mock import patch, AsyncMock

import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_cdek_order_partial_update(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    body = {
        'receiver_name': 'Test receiver',
    }

    response = await client.patch(
        url='/v1/order/1',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 400
    assert response.json().get('detail') == 'Can not update a cdek order'
