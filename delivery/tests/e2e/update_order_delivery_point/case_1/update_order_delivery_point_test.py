import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_query_update_delivery_point(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    order_new_delivery_point,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.patch(
        url='/v2/order/1/delivery_point',
        headers={'Authorization': 'Bearer ' + access_token},
        data=order_new_delivery_point,
    )
    assert response.status_code == 200
