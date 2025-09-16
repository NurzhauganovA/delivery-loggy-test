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
    assert order_delivery_status['status'] == 'cancelled'
    assert order_delivery_status['reason'] == 'For testing purpose only'


@pytest.mark.asyncio
@freeze_time('2025-07-22 09:16:27.181389+00:00')
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_record_history_after_order_cancel(
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

    order_id = 3
    body = {
        'reason': 'For testing purpose only',
    }
    response = await client.put(
        url=f'/v1/order/{order_id}/cancel',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 200

    history_response = await client.get(
        url='/v1/history/list',
        headers={'Authorization': 'Bearer ' + access_token},
        params={
            'model_type': 'Order',
            'model_id': order_id,
        }
    )
    assert history_response.status_code == 200
    history_data = history_response.json().get('items')
    action_data = history_data[0].get('action_data') if history_data else dict()
    delivery_status = action_data.get('delivery_status') if action_data else dict()
    assert delivery_status.get('status') == 'cancelled'
    assert delivery_status.get('reason') == 'For testing purpose only'


@pytest.mark.asyncio
@freeze_time('2025-07-22 09:16:27.181389+00:00')
@patch('api.models.publisher.__publish')
async def test_send_status_after_order_cancel(
    publisher: AsyncMock,
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

    order_id = 4
    body = {
        'reason': 'For testing purpose only',
    }
    await client.put(
        url=f'/v1/order/{order_id}/cancel',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )

    publisher.assert_awaited_once_with(
        channel='send-to-celery',
        message={
            'kwargs': {
                'data': {
                    'comment': 'For testing purpose only',
                    'status': OrderDeliveryStatus.CANCELLED,
                    'status_datetime': '2025-07-22 14:16:27.181389+00:00',
                },
                'headers': {},
                'url': 'https://example-partner.kz/api/loggy/callbacks/set-status/3928b9e9-91a5-481c-88d2-9980a3f75f10?token=f0ce3fd77de24e0a9b07e7a02da2aa02'
            },
            'task_name': 'send-status'
        }
    )


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
        data=body,
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
        data=body,
    )
    assert response.status_code == 400
    assert response.json() == {'detail': 'Already completed', 'status': 'bad_request', 'status_code': 400}

