import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_get_delivery_graph(
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
        Получение деливери графа в заявке
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.get(
        url='/v2/order/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data.get('deliverygraph')
    assert response_data['deliverygraph'].get('graph') == expected
