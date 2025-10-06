import pytest

from api.dependencies import OrderDefaultFilterV2
from api.models import Order
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
async def test_default_filter_v2_by_logist(
    logist,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    dep = OrderDefaultFilterV2()
    q_objs = await dep(current_user=logist)

    orders = await Order.filter(*q_objs)
    assert len(orders) == 3

    for o in orders:
        assert o.courier_service in ('cdek', None)


@pytest.mark.asyncio
async def test_default_filter_v2_by_support(
    support,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    dep = OrderDefaultFilterV2()
    q_objs = await dep(current_user=support)

    orders = await Order.filter(*q_objs)
    assert len(orders) == 3

    for o in orders:
        assert o.courier_service in ('cdek', None)


@pytest.mark.asyncio
async def test_default_filter_v2_by_general_call_center_manager(
    general_ccm,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    dep = OrderDefaultFilterV2()
    q_objs = await dep(current_user=general_ccm)

    orders = await Order.filter(*q_objs)
    assert len(orders) == 3

    for o in orders:
        assert o.courier_service in ('cdek', None)
