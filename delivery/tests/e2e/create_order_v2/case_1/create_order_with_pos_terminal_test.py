import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_order_create_with_product_payload(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    order_create_with_pos_terminal_body,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    expected,
):
    """
        Создание заявки с продуктом pos_terminal
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.post(
        url='/v2/order',
        headers={'Authorization': 'Bearer ' + access_token},
        data=order_create_with_pos_terminal_body,
    )
    assert response.status_code == 201
    assert response.json() == {'id': 1}

    response = await client.get(
        url='/v2/order/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    assert response.json() == expected