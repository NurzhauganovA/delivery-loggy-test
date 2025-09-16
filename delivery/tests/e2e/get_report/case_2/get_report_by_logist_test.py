import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_get_statistics_by_supervisor(
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

    data = {
        'filtering': {
        }
    }

    response = await client.post(
        url='/v1/order/report',
        headers={'Authorization': 'Bearer ' + access_token},
        json=data
    )
    assert response.status_code == 200
