import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_get_order_list_v1_filter_by_courier_service_by_logist(
        client,
        credentials,
        profile_logist,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)
    access_token = await get_access_token_v1(client, credentials, profile_logist)

    params = {
        'courier_service': 'cdek',
    }

    response = await client.get(
        url='/v1/order/list',
        headers={'Authorization': 'Bearer ' + access_token},
        params=params,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get('total') == 2



@pytest.mark.asyncio
async def test_get_order_list_v1_filter_by_courier_service_by_support(
        client,
        credentials,
        profile_support,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)
    access_token = await get_access_token_v1(client, credentials, profile_support)

    params = {
        'courier_service': 'cdek',
    }

    response = await client.get(
        url='/v1/order/list',
        headers={'Authorization': 'Bearer ' + access_token},
        params=params,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get('total') == 2



@pytest.mark.asyncio
async def test_get_order_list_v1_filter_by_courier_service_by_general_call_center_manager(
        client,
        credentials,
        profile_general_call_center_manager,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)
    access_token = await get_access_token_v1(client, credentials, profile_general_call_center_manager)

    params = {
        'courier_service': 'cdek',
    }

    response = await client.get(
        url='/v1/order/list',
        headers={'Authorization': 'Bearer ' + access_token},
        params=params,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get('total') == 2
