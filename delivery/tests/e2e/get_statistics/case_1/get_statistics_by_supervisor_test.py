from datetime import datetime, timedelta

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
    expected,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    params = {
        'from_date': datetime.now() - timedelta(days=1),
        'to_date': datetime.now() + timedelta(days=1),
    }

    response = await client.get(
        url='/v1/statistics',
        headers={
            'Authorization': 'Bearer ' + access_token,
            'X-Locale': 'ru',
        },
        params=params,
    )
    assert response.status_code == 200
    assert response.json() == expected
