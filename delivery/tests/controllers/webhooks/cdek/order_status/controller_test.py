import pytest
from tortoise.exceptions import DoesNotExist

from api import models
from api.controllers.webhooks.cdek import handle_order_status
from api.schemas.webhooks.cdek import OrderStatusRequest
from tests.fixtures.database import (
    db,
    run_pre_start_sql_script,
)


@pytest.mark.asyncio
async def test_save_status(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    # Вызываем метод обработки статуса заявки CDEK
    await handle_order_status(
        request=OrderStatusRequest.parse_obj(
            {
                "uuid": "72753031-1820-4f99-9240-aab139f05ca5",
                "attributes": {
                    "code": "RECEIVED_AT_SHIPMENT_WAREHOUSE",
                }
            }
        )
    )

    # Проверим, сохранили ли мы переданный статус в таблицу
    courier_service_status = await models.CourierServiceStatus.filter(order_id=1).first()
    courier_service_status.status = "RECEIVED_AT_SHIPMENT_WAREHOUSE"
