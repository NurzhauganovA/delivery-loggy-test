import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_get_user_list_by_call_center_manager(
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

    response = await client.get(
        url='/v1/user/list',
        params={
            'profile_type': 'courier',
            'page': 1,
            'page_limit': 50,
        },
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data['items']) == 3


@pytest.mark.asyncio
async def test_get_user_list_by_call_center_manager_empty_result(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    """
        Фильтрация по городу, ответ пустой

        Пользователь не может видеть курьеров города Москва.
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.get(
        url='/v1/user/list',
        params={
            'profile_type': 'courier',
            'city_id': 4,
            'page': 1,
            'page_limit': 50,
        },
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    response_data = response.json()

    assert response_data == {'current_page': 1, 'items': [], 'total': 0, 'total_pages': 0}
