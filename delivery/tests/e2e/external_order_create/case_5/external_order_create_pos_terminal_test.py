import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_external_order_create_pos_terminal(
        client,
        body,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key,
):
    """
        Создание заявки с продуктом "POS Терминал"
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    response = await client.post(
        url='/v1/external/order/create',
        data=body,
        params={
            'api_key': api_key,
        }
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data.get('product')

    product = response_data['product']
    assert product.get('type') == 'pos_terminal'
    assert product.get('attributes') == {
        "is_installment_enabled": False,
        "is_installment_limit": True,
        "company_name": "ТОО Рога и Копыта",
        "merchant_id": "12345678",
        "terminal_id": "12345678",
        "store_name": "MyMart",
        "branch_name": "Основной MyMart",
        "mcc_code": "GGG1",
        'model': None,
        'oked_code': 'QWERTY123',
        'oked_text': 'OKED SAMPLE TEXT',
        'serial_number': None,
        'request_number_ref': '123456789',
        'inventory_number': '123456789',
        'sum': 10000.1
    }



@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_external_order_create_pos_terminal_validation_error(
        client,
        invalid_body,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key,
):
    """
        Создание заявки с продуктом "POS Терминал", ошибка валидации
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    response = await client.post(
        url='/v1/external/order/create',
        data=invalid_body,
        params={
            'api_key': api_key,
        }
    )
    assert response.status_code == 422
