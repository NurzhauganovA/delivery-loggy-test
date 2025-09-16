from unittest.mock import patch, AsyncMock

import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_order_noncall_with_comment(
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
        'comment': 'For testing purpose only',
    }

    response = await client.put(
        url='/v1/order/1/noncall',
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
    delivery_status = order_get_response.json().get('delivery_status')
    assert delivery_status is not None
    assert delivery_status.get('status') == 'noncall'
    assert delivery_status.get('comment') == body['comment']


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_order_noncall_without_comment(
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

    body = {}

    response = await client.put(
        url='/v1/order/2/noncall',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'loc': [
                    'body', 'comment'],
                'msg': 'field required',
                'type': 'value_error.missing'
            }
        ]
    }


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_order_noncall_with_too_short_comment(
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
        'comment': 'For tes',
    }

    response = await client.put(
        url='/v1/order/2/noncall',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'ctx': {'limit_value': 10},
                'loc': ['body', 'comment'],
                'msg': 'ensure this value has at least 10 characters',
                'type': 'value_error.any_str.min_length'
            }
        ]
    }


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_order_noncall_with_too_long_comment(
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
        'comment': "1" * 1001,
    }

    response = await client.put(
        url='/v1/order/2/noncall',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'ctx': {'limit_value': 1000},
                'loc': ['body', 'comment'],
                'msg': 'ensure this value has at most 1000 characters',
                'type': 'value_error.any_str.max_length'
            }
        ]
    }
