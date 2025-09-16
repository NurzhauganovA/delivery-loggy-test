import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_card_product_type_and_pos_terminal_payload(
        client,
        body_card,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key,
):
    """
        Создание заявки с продуктом card но с неверным product_type
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    response = await client.post(
        url='/v1/external/order/create',
        data=body_card,
        params={
            'api_key': api_key,
        }
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['pan'], 'msg': 'field required', 'type': 'value_error.missing'}]}


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_pos_terminal_product_type_and_card_payload(
        client,
        body_pos_terminal,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key,
):
    """
        Создание заявки с продуктом pos_terminal но с неверным payload
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    response = await client.post(
        url='/v1/external/order/create',
        data=body_pos_terminal,
        params={
            'api_key': api_key,
        }
    )
    assert response.status_code == 422
