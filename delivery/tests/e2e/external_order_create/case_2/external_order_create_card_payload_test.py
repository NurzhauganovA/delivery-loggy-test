import pytest
from freezegun import freeze_time

from api.models import PAN
from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_external_order_create_card_payload(
        client,
        body,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key,
):
    """
        Создание заявки с продуктом "Карта", но без product_type
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
    assert product.get('type') == 'card'
    assert product.get('attributes') == {
        "pan": "5269********1234",
        "pan_suffix": "1234",
    }


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_external_order_create_card_payload_and_card_product_type(
        client,
        body,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key,
):
    """
        Создание заявки с продуктом "Карта" c product_type = card
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
    assert product.get('type') == 'card'
    assert product.get('attributes') == {
        "pan": "5269********1234",
        "pan_suffix": "1234",
    }
