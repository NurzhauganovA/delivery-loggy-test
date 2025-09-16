import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@freeze_time('2025-07-18T11:42:00+05:00')
async def test_set_actual_delivery_datetime_on_postcontrol(
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

    response = await client.put(
        url=f'/v1/order/{order_id}/status',
        headers={'Authorization': 'Bearer ' + access_token},
        params={
        'status_id': 12,
    },
    )
    assert response.status_code == 200

    order_response = await client.get(
        url=f'/v1/order/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert order_response.status_code == 200
    assert order_response.json().get('actual_delivery_datetime') == '2025-07-18T11:42:00+00:00'


@pytest.mark.asyncio
@freeze_time('2025-07-18T11:42:00+05:00')
async def test_set_actual_delivery_datetime_on_postcontrol_v2(
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

    response = await client.put(
        url=f'/v1/order/{order_id}/status',
        headers={'Authorization': 'Bearer ' + access_token},
        params={
        'status_id': 12,
        },
    )
    assert response.status_code == 200

    order_response = await client.get(
        url=f'/v2/order/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert order_response.status_code == 200
    assert order_response.json().get('actual_delivery_datetime') == '2025-07-18T11:42:00+00:00'
