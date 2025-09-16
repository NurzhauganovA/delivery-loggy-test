import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_order_comment_create(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    """
        Создание комментария заявке
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    order_id = 1

    response = await client.post(
        url=f'/v2/order/{order_id}/comments',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'text': 'Sample comment text',
        },
    )
    assert response.status_code == 201
    assert response.json() == {'id': 1}


@pytest.mark.asyncio
@freeze_time('2025-04-14T12:00:00Z')
async def test_order_history_record_on_comment_create(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    expected_history_record,
):
    await run_pre_start_sql_script(pre_start_sql_script)
    access_token = await get_access_token_v1(client, credentials, profile_data)

    order_id = 1

    response = await client.post(
        url=f'/v2/order/{order_id}/comments',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'text': 'Sample comment text',
        },
    )
    assert response.status_code == 201

    history_response = await client.get(
        url=f'/v1/history/list?model_type=Order&model_id={order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert history_response.status_code == 200
    assert history_response.json() == expected_history_record


@pytest.mark.asyncio
async def test_order_comment_create_for_non_existing_order(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    """
        Создание комментария несуществующей заявке
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    order_id = 100

    response = await client.post(
        url=f'/v2/order/{order_id}/comments',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'text': 'Sample comment text',
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Order does not exist',
        'status': 'bad_request',
        'status_code': 400,
    }
