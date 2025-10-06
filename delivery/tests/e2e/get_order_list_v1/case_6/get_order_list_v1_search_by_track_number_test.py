import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_get_order_list_v1_search_by_track_number(
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

    params = {
        'search_type': 'track_number',
        'search': '1234567',
    }

    response = await client.get(
        url='/v1/order/list',
        headers={'Authorization': 'Bearer ' + access_token},
        params=params,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get('total') == 1


@pytest.mark.asyncio
async def test_get_order_search_by_track_number_empty_list(
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

    params = {
        'search_type': 'track_number',
        'search': 'asdfasdf',
    }

    response = await client.get(
        url='/v1/order/list',
        headers={'Authorization': 'Bearer ' + access_token},
        params=params,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get('total') == 0
