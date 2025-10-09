import pytest
from datetime import datetime

from tests.e2e.get_order_v2.case_12.conftest import orders_insert_script, order_statuses_insert_script
from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_get_order_with_cdek_sub_statuses(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        expected_sub_statuses,
):
    """
    Проверка получения саб-статусов СДЕК в заявке
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.get(
        url='/v2/order/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )

    assert response.status_code == 200

    response_data = response.json()

    # Проверяем наличие статусов
    assert 'statuses' in response_data
    assert len(response_data['statuses']) > 0

    # Ищем статус СДЕК
    cdek_status = None
    for status_item in response_data['statuses']:
        if status_item['status']['slug'] == 'cdek':
            cdek_status = status_item
            break

    assert cdek_status is not None, "СДЕК статус не найден"

    # Проверяем наличие саб-статусов
    assert 'sub_statuses' in cdek_status
    assert len(cdek_status['sub_statuses']) == 3

    # Проверяем структуру саб-статусов
    for i, sub_status in enumerate(cdek_status['sub_statuses']):
        assert 'name' in sub_status
        assert 'created_at' in sub_status
        assert sub_status['name'] == expected_sub_statuses[i]['name']


@pytest.mark.asyncio
async def test_get_order_without_cdek_sub_statuses(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        run_pre_start_sql_script,
):
    """
    Проверка что у не-СДЕК статусов нет саб-статусов
    """
    # SQL без courier_service_status записей
    sql_script = " ".join([
        # ... базовые скрипты ...
        orders_insert_script(),
        order_statuses_insert_script(),
    ])

    await run_pre_start_sql_script(sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.get(
        url='/v2/order/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )

    assert response.status_code == 200
    response_data = response.json()

    # Проверяем что у обычных статусов нет саб-статусов или пустой массив
    for status_item in response_data['statuses']:
        if status_item['status']['slug'] != 'cdek':
            assert status_item.get('sub_statuses', []) == []