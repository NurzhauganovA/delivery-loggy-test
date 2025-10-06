import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_get_order_list_v2_filter_by_courier_service(
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
        'courier_service': 'cdek',
    }

    response = await client.get(
        url='/v2/order/list',
        headers={'Authorization': 'Bearer ' + access_token},
        params=params,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get('total') == 2
