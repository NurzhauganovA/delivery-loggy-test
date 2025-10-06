import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_mass_set_status_of_cdek_orders(
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

    json = {
        'status_id': 2,
        'order_id_list': [1, 2, 3],
    }

    response = await client.put(
        url='/v1/order/mass-set-status',
        headers={'Authorization': 'Bearer ' + access_token},
        json=json,
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data.get('detail') == 'Can not assign a courier to cdek orders'
