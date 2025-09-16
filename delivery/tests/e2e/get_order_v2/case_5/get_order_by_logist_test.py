import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_get_order_by_logist(
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

    response = await client.get(
        url='/v2/order/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_get_order_by_logist_not_found(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    """
    Try to get an order with an unrelated city_id to the logist.
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.get(
        url='/v2/order/4',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 404
    response_data = response.json()
    assert 'detail' in response_data
    assert response_data['detail'] == 'Order with provided ID: 4 was not found'
