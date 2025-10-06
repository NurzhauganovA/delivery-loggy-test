import pytest
from tortoise.expressions import RawSQL

from api.dependencies import OrderDefaultFilter
from api.models import Order
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.parametrize(
    'profile_name',
    [
        'bank_manager',
        'branch_manager',
        'call_center_manager',
        'courier',
        'dispatcher',
        'manager',
        'partner_branch_manager',
        'service_manager',
        'sorter',
        'supervisor',
    ],
)
@pytest.mark.asyncio
async def test_default_filter_v1_by_profiles(
    profile_name,
    request,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)
    profile_data  = request.getfixturevalue(profile_name)
    dep = OrderDefaultFilter()
    q_objs = await dep(current_user=profile_data)

    orders = await Order.annotate(
        has_ready_for_shipment=RawSQL('true'),
    ).filter(*q_objs)
    assert len(orders) == 0
