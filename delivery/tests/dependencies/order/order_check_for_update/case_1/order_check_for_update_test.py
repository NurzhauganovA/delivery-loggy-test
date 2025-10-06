import pytest

from api import exceptions
from api.dependencies import order_check_for_update
from api.models import Order
from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
async def test_cdek_order_partial_update(
    client,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_obj = await Order.get(id=1)
    with pytest.raises(exceptions.HTTPBadRequestException, match='Can not update a cdek order'):
        await order_check_for_update(order_obj=order_obj)
