import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_pagination(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    """
        Получения заявок используя пагинацию
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    # Получение первой страницы
    response = await client.get(
        url='/v2/order/list',
        params={
            'page': 1,
            'page_limit': 2,
        },
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data.get('items', [])) == 2
    assert data.get('current_page') == 1
    assert data.get('total_pages') == 2
    assert data.get('total') == 3

    # Получение второй страницы
    response = await client.get(
        url='/v2/order/list',
        params={
            'page': 2,
            'page_limit': 2,
        },
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data.get('items', [])) == 1
    assert data.get('current_page') == 2
    assert data.get('total_pages') == 2
    assert data.get('total') == 3

