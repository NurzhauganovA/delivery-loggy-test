import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
async def test_restore_order_with_product_and_with_scan_card_step(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    """
        Сброс заявки с шагом "Сканирование карты" в деливери графе
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    # Получим заявку, увидим что у нее есть продукт
    response = await client.get(
        url='/v1/order/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    assert response.json().get('product') == {
        'attributes': {
            'pan': '1234********1234',
            'pan_suffix': '1234'
        },
        'id': 1,
        'name': 'Какая то карта',
        'type': 'card'
    }

    # Сбросим эту заявку
    response = await client.patch(
        url='/v1/order/1/restore',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            "courier_id": None,
            "delivery_status": {},
            "delivery_datetime": "2025-09-30T06:42:00.000Z",
        }
    )
    assert response.status_code == 200

    # Получим эту заявку еще раз, увидим что продукт удалился
    response = await client.get(
        url='/v1/order/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    assert response.json().get('product') == {
        'attributes': {
            'pan': '1234********1234',
            'pan_suffix': '1234'
        },
        'id': 1,
        'name': 'Какая то карта',
        'type': 'card'
    }


@pytest.mark.asyncio
async def test_restore_order_with_product(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        expected_pos_terminal_product,
):
    """
        Сброс заявки с созданным продуктом
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    # Получим заявку, увидим что у нее есть продукт
    response = await client.get(
        url='/v1/order/2',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    assert response.json().get('product') == expected_pos_terminal_product

    # Сбросим эту заявку
    response = await client.patch(
        url='/v1/order/2/restore',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            "courier_id": None,
            "delivery_status": {},
            "delivery_datetime": "2025-09-30T06:42:00.000Z",
        }
    )
    assert response.status_code == 200

    # Получим эту заявку еще раз, увидим что продукт не удалился
    response = await client.get(
        url='/v1/order/2',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    assert response.json().get('product') == expected_pos_terminal_product
