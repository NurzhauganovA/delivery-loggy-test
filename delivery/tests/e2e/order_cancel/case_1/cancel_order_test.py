from unittest.mock import patch, AsyncMock

import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_cancel_order_for_delivery_datetime_non_lost(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    expected,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    body = {
        'reason': 'For testing purpose only',
    }

    response = await client.put(
        url='/v1/order/1/cancel',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.json() is None
    assert response.status_code == 200

    order_get_response = await client.get(
        url='/v1/order/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert order_get_response.status_code == 200
    assert order_get_response.json().get('delivery_datetime') is not None
