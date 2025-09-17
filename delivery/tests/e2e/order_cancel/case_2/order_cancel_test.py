from unittest.mock import patch, AsyncMock

import pytest
from freezegun import freeze_time

from api.enums import OrderDeliveryStatus
from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@freeze_time('2025-07-22 09:16:27.181389+00:00')
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_order_cancel(
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

    order_id = 1
    body = {
        'reason': 'For testing purpose only',
    }
    response = await client.put(
        url=f'/v1/order/{order_id}/cancel',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 200
    assert response.json() is None

    order_get_response = await client.get(
        url=f'/v1/order/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert order_get_response.status_code == 200
    order_response_data = order_get_response.json()
    order_delivery_status = order_response_data['delivery_status']
    assert order_delivery_status['status'] == 'requested_to_cancel'
    assert order_delivery_status['reason'] == 'For testing purpose only'


@pytest.mark.asyncio
async def test_order_cancel_with_non_existent_order(
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

    order_id = 100
    body = {
        'reason': 'For testing purpose only',
    }
    response = await client.put(
        url=f'/v1/order/{order_id}/cancel',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 400
    assert response.json() == {'detail': 'Not found', 'status': 'bad_request', 'status_code': 400}


@pytest.mark.asyncio
async def test_order_cancel_with_already_delivered_order(
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

    order_id = 2
    body = {
        'reason': 'For testing purpose only',
    }
    response = await client.put(
        url=f'/v1/order/{order_id}/cancel',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 400
    assert response.json() == {'detail': 'Already completed', 'status': 'bad_request', 'status_code': 400}
