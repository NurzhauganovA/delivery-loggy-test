from unittest.mock import patch, AsyncMock

import pytest
from freezegun import freeze_time

from api.enums import OrderDeliveryStatus
from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_order_request_to_cancel(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    """
    Тестируем отправку запроса на отмену заявки с какой-нибудь любой причиной.
    У заявки не должны быть фотографии для отмены, и фактически тоже не имеются.
    """
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
    assert order_delivery_status['status'] == 'requested_to_cancel'
    assert order_delivery_status['reason'] == 'For testing purpose only'
    assert order_delivery_status['comment'] == 'For testing purpose only'


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_order_accept_cancel_without_image(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    """
    Тестируем подтверждения отмены заявки с какой-нибудь любой причиной.
    Причина должен остаться такой же, как при отправке запроса на отмену.
    У заявки не должны быть фотографии для отмены, фактически тоже имеются.

    """
    await run_pre_start_sql_script(pre_start_sql_script)
    access_token = await get_access_token_v1(client, credentials, profile_data)

    order_id = 6

    response = await client.put(
        url=f'/v1/order/{order_id}/accept-cancel',
        headers={
            'Authorization': 'Bearer ' + access_token,
        },
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
    assert order_delivery_status['status'] == 'cancelled'
    assert order_delivery_status['reason'] == 'For testing purpose only'
    assert order_delivery_status['comment'] == 'For testing purpose only'


@pytest.mark.asyncio
@pytest.mark.freeze_uuids
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_order_request_to_cancel_without_image(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    """
    Тестируем отправку запроса на отмену заявки с причиной "возврат по истечению срока".
    У заявки должны быть фотографии для отмены, но фактически не имеются.
    Так что получаем ошибку со статусом 400.
    """
    await run_pre_start_sql_script(pre_start_sql_script)
    access_token = await get_access_token_v1(client, credentials, profile_data)

    order_id = 2
    body = {
        'reason': 'возврат по истечению срока',
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
        'detail': 'At least one image is required',
        'status': 'bad_request',
        'status_code': 400,
    }


@pytest.mark.asyncio
@pytest.mark.freeze_uuids
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_order_request_to_cancel_image_not_allowed(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    """
    Тестируем отправку запроса на отмену заявки с какой-нибудь любой причиной.
    У заявки не должны быть фотографии для отмены, но фактически имеются.
    Так что получаем ошибку со статусом 400.
    """
    await run_pre_start_sql_script(pre_start_sql_script)
    access_token = await get_access_token_v1(client, credentials, profile_data)

    order_id = 5
    body = {
        'reason': 'Some reason',
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
        'detail': 'Image is not allowed for this cancellation reason',
        'status': 'bad_request',
        'status_code': 400,
    }


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_record_history_after_order_accept_cancel(
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
    response = await client.put(
        url=f'/v1/order/{order_id}/accept-cancel',
        headers={'Authorization': 'Bearer ' + access_token},
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
    assert delivery_status.get('reason') == 'возврат по истечению срока'


@pytest.mark.asyncio
@freeze_time('2025-07-22 09:16:27.181389+00:00')
@patch('api.models.publisher.__publish')
async def test_send_status_after_order_accept_cancel(
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
    await client.put(
        url=f'/v1/order/{order_id}/accept-cancel',
        headers={'Authorization': 'Bearer ' + access_token},
    )

    publisher.assert_awaited_once_with(
        channel='send-to-celery',
        message={
            'kwargs': {
                'data': {
                    'comment': 'возврат по истечению срока',
                    'status': OrderDeliveryStatus.CANCELLED,
                    'status_datetime': '2025-07-22 14:16:27.181389+00:00',
                },
                'headers': {},
                'url': 'https://example-partner.kz/api/loggy/callbacks/set-status/1234?token=1234'
            },
            'task_name': 'send-status'
        }
    )
