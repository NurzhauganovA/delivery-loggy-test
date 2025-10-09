from unittest.mock import patch, AsyncMock

import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_with_zeros_in_coordinates(
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

    body = {
        'comment': 'For testing purpose only',
    }

    response = await client.put(
        url='/v1/order/1/noncall',
        headers={'Authorization': 'Bearer ' + access_token},
        json=body,
    )
    assert response.json() is None
    assert response.status_code == 200
