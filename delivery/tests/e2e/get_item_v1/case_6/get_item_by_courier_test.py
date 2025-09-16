import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_get_item_by_courier(
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
        url='/v1/item/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_get_item_by_courier_with_empty_message_for_noncall(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        expected_empty_non_call_message,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.get(
        url='/v1/item/2',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    assert response.json() == expected_empty_non_call_message
