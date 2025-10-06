import pytest
from freezegun import freeze_time

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
@freeze_time("2025-04-14T12:00:00Z")
async def test_external_order_create(
        client,
        body,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key,
        expected,
):
    """
        Создание заявки с внешнего API.
        Без product_type и без payload
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
    assert response.json() == expected
