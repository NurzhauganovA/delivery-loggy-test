from unittest.mock import patch, AsyncMock

import pytest

from api.enums import OrderDeliveryStatus
from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@pytest.mark.freeze_uuids
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_order_request_to_cancel(
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

    order_id = 1
    body = {
        'reason': 'For testing purpose only',
        'comment': 'For testing purpose only',

    }

    response = await client.put(
        url=f'/v1/order/{order_id}/cancel',
        headers={
            'Authorization': 'Bearer ' + access_token,
        },
        json=body,
    )
    assert response.json() is None
    assert response.status_code == 200

    order_get_response = await client.get(
        url=f'/v1/order/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert order_get_response.status_code == 200
    order_response_data = order_get_response.json()
    order_delivery_status = order_response_data['delivery_status']
    assert order_delivery_status['status'] == OrderDeliveryStatus.REQUESTED_TO_CANCEL
    assert order_delivery_status['reason'] == 'For testing purpose only'
    assert order_delivery_status['comment'] == 'For testing purpose only'


@pytest.mark.asyncio
@pytest.mark.freeze_uuids
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_order_request_to_cancel_with_no_photo(
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

    order_id = 2
    body = {
        'reason': 'For testing purpose only',
        'comment': 'For testing purpose only',

    }

    response = await client.put(
        url=f'/v1/order/{order_id}/cancel',
        headers={
            'Authorization': 'Bearer ' + access_token,
        },
        json=body,
    )
    assert response.status_code == 400

    assert response.json() == {
        'detail': 'At least one photo is required',
        'status': 'bad_request',
        'status_code': 400,
    }
