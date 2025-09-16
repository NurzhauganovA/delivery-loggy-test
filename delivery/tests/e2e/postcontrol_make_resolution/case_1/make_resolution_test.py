from unittest.mock import patch, AsyncMock

import pytest
from freezegun import freeze_time

from api.enums import PostControlResolution
from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@freeze_time('2025-07-18 11:42:00+05:00')
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_postcontrol_make_resolution_mark_order_as_delivered(
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
    body = [
        {
            'id': 1,
            'resolution': 'accepted',
        },
        {
            'id': 2,
            'resolution': 'accepted',
        },
        {
            'id': 3,
            'resolution': 'accepted',
        },
    ]
    response = await client.put(
        url=f'/v1/post-control/make-resolution',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.json() == expected
    assert response.status_code == 200

    order_get_response = await client.get(
        url=f'/v1/order/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert order_get_response.status_code == 200
    order_response_data = order_get_response.json()
    order_delivery_status = order_response_data['delivery_status']
    assert order_delivery_status['status'] == 'is_delivered'


@pytest.mark.asyncio
@freeze_time('2025-07-18 11:42:00+05:00')
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_record_history_on_postcontrol_make_resolution(
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

    order_id = 4
    body = [
        {
            'id': 7,
            'resolution': 'accepted',
        },
        {
            'id': 8,
            'resolution': 'accepted',
        },
        {
            'id': 9,
            'resolution': 'accepted',
        },
    ]
    await client.put(
        url=f'/v1/post-control/make-resolution',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )

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
    assert action_data == {'post-control': PostControlResolution.ACCEPTED}


@pytest.mark.asyncio
@freeze_time('2025-07-18 11:42:00+05:00')
@patch('api.models.publisher.__publish')
async def test_send_callbacks_on_postcontrol_make_resolution(
    publisher: AsyncMock,
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    expected,
    celery_calls,
):
    await run_pre_start_sql_script(pre_start_sql_script)
    access_token = await get_access_token_v1(client, credentials, profile_data)

    body = [
        {
            'id': 10,
            'resolution': 'accepted',
        },
        {
            'id': 11,
            'resolution': 'accepted',
        },
        {
            'id': 12,
            'resolution': 'accepted',
        },
    ]
    await client.put(
        url=f'/v1/post-control/make-resolution',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )

    assert publisher.mock_calls == celery_calls


@pytest.mark.asyncio
async def test_postcontrol_make_resolution_decline_some_documents(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    expected_decline,
):
    await run_pre_start_sql_script(pre_start_sql_script)
    access_token = await get_access_token_v1(client, credentials, profile_data)

    order_id = 1
    body = [
        {
            'id': 1,
            'resolution': 'declined',
            'comment': 'Fix it'
        },
        {
            'id': 2,
            'resolution': 'declined',
            'comment': 'Fix it'
        },
        {
            'id': 3,
            'resolution': 'accepted',
        },
    ]
    response = await client.put(
        url=f'/v1/post-control/make-resolution',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.json() == expected_decline
    assert response.status_code == 200

    order_get_response = await client.get(
        url=f'/v1/order/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert order_get_response.status_code == 200
    order_response_data = order_get_response.json()
    order_delivery_status = order_response_data['delivery_status']
    assert order_delivery_status['status'] == 'being_finalized'


@pytest.mark.asyncio
async def test_postcontrol_make_resolution_with_non_existent_document(
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

    body = [
        {
            'id': 100,
            'resolution': 'accepted',
        },
    ]
    response = await client.put(
        url=f'/v1/post-control/make-resolution',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Post-control document with provided ID: 100 was not found',
        'status': 'not-found',
        'status_code': 404,
    }


@pytest.mark.asyncio
async def test_postcontrol_make_resolution_with_for_order_at_photo_capturing_status(
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

    body = [
        {
            'id': 4,
            'resolution': 'declined',
            'comment': 'Fix it'
        },
        {
            'id': 5,
            'resolution': 'declined',
            'comment': 'Fix it'
        },
        {
            'id': 6,
            'resolution': 'accepted',
        },
    ]
    response = await client.put(
        url=f'/v1/post-control/make-resolution',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )

    assert response.json() == {
        'detail': [
            {
                'loc': ['body', '__root__'],
                'msg': 'Can not make resolution in this stage',
                'type': 'validation_error'
            }
        ]
    }
    assert response.status_code == 422
