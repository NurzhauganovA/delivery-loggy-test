import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_create_sep_unempossed(
        client,
        body,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key,
        expected,
):
    """
        Создание заявки с продуктом SEP-неименные
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    response = await client.post(
        url='/v1/external/order/create',
        json=body,
        params={
            'api_key': api_key,
        }
    )
    assert response.status_code == 200
    response_data = response.json()
    client_code = response_data['product']['attributes']['client_code']
    assert client_code == expected


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_create_sep_unempossed_validation_error(
        client,
        invalid_body,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key,
):
    """
        Создание заявки с продуктом SEP-неименные, ошибка валидации
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    response = await client.post(
        url='/v1/external/order/create',
        json=invalid_body,
        params={
            'api_key': api_key,
        }
    )
    assert response.status_code == 422
