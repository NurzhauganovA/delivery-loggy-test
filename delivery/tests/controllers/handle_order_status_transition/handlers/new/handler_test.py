import pytest

from api import models
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
async def test_changing_status_to_new(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        handler,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    new_status = await models.Status.get(code='new')

    order = await models.Order.get(id=1)
    assert order.current_status_id != new_status.id

    await handler.handle(
        order_obj=order,
        status=new_status,
    )

    order = await models.Order.get(id=1)
    assert order.current_status_id == new_status.id
