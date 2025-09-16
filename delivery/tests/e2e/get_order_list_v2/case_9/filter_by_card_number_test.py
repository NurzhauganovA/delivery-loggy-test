import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_filter_by_card_number(
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
        Фильтрация по PAN карты (последних 4 символа), получаем ответ

        С таким pan_suffix две карты
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.get(
        url='/v2/order/list',
        params={
            'search': '1234',
            'search_type': 'card_number',
        },
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_filter_by_card_number_no_result(
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
        Фильтрация по PAN карты (последних 4 символа), ответ пустой

        С таким pan_suffix нет карт
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.get(
        url='/v2/order/list',
        params={
            'search': '5555',
            'search_type': 'card_number',
        },
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    assert response.json() == {'items': [], 'current_page': 1, 'total_pages': 0, 'total': 0}
