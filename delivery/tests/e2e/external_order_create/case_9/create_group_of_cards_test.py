import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_create_group_of_cards(
        client,
        body,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key,
):
    """
        Создание заявки с продуктом "ЗП проект"
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
    assert product.get('type') == 'group_of_cards'
    assert product.get('name') == 'Групповая доставка ЗП карт'
    assert product.get('attributes') == [
        {
          "id": 0,
          "pan": "5269********1234",
          "iin": "990208350377",
          "fio": "Иванов Иван"
        },
        {
          "id": 1,
          "pan": "5269********1234",
          "iin": "990208350377",
          "fio": "Иванов Иван"
        },
        {
          "id": 2,
          "pan": "5269********1234",
          "iin": "990208350377",
          "fio": "Иванов Иван"
        }
      ]




@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_create_group_of_cards_validation_error(
        client,
        invalid_body,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key,
):
    """
        Создание заявки с продуктом "ЗП проект", ошибка валидации
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
