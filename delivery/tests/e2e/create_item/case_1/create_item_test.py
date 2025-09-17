import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_create_item(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    create_item_body,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    expected_default_postcontrol_cancellation_configs,
):
    """
        Создание продукта (item)
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.post(
        url='/v1/item',
        headers={'Authorization': 'Bearer ' + access_token},
        json=create_item_body,
    )
    assert response.status_code == 201
    assert response.json().get('postcontrol_cancellation_configs') == expected_default_postcontrol_cancellation_configs


