import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_get_order_product(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    """
        Получение продукта у заявки
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.get(
        url='/v1/order/1/product/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data.get('id') == 1
    assert response_data.get('order_id') == 1
    assert response_data.get('type')
    assert response_data.get('attributes')


@pytest.mark.asyncio
async def test_get_order_product_not_found(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    """
        Ошибка продукт не найден
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.get(
        url='/v1/order/1/product/2',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'product not found', 'status': 'not_found', 'status_code': 404}
