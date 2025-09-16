import pytest

from api import models
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
async def test_changing_status_to_card_returned_to_bank(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    card_returned_to_bank_status = await models.Status.get(code='card_returned_to_bank')

    order = await models.Order.get(id=1)
    assert order.current_status_id != card_returned_to_bank_status.id

    await handler.handle(
        order_obj=order,
        status=card_returned_to_bank_status,
    )

    order = await models.Order.get(id=1)
    assert order.current_status_id == card_returned_to_bank_status.id
