import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_get_order_with_cdek_substatuses(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        expected,
):
    """
        Получение заявки для CRM
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.get(
        url='/v2/crm/order/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    print("RESPONSE:", response.json())
    statuses = response.json().get('statuses')

    assert response.status_code == 200
    assert statuses == expected["statuses"]