import pytest

from api import models
from api.controllers.update_order_delivery_point import exceptions
from tests.fixtures.database import (
    db,
    run_pre_start_sql_script,
)


@pytest.mark.asyncio
async def test_update_delivery_point_valid_courier(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    request_and_expected,
    update_order_delivery_point,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    request, expected = request_and_expected('valid_courier')
    user_id = request['user_id']
    order_id = request['order_id']
    user_role = request['user_role']
    data = request['data']

    await update_order_delivery_point.init(user_id, order_id, user_role, data)

    order_obj = await models.Order.get(
        id=order_id
    ).prefetch_related(
        'delivery_point'
    ).prefetch_related('status_set')

    status = await order_obj.current_status.first()
    delivery_point = await order_obj.delivery_point.first()

    assert order_obj.comment == expected['comment']
    assert order_obj.delivery_status['status'] == expected['delivery_status']
    assert status.slug == expected['current_status']
    assert float(delivery_point.latitude) == expected['delivery_point']['latitude']
    assert float(delivery_point.longitude) == expected['delivery_point']['longitude']
    assert delivery_point.address == expected['delivery_point']['address']


@pytest.mark.asyncio
async def test_update_delivery_point_valid_supervisor(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    request_and_expected,
    update_order_delivery_point,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    request, expected = request_and_expected('valid_supervisor')
    user_id = request['user_id']
    order_id = request['order_id']
    user_role = request['user_role']
    data = request['data']

    await update_order_delivery_point.init(user_id, order_id, user_role, data)

    order_obj = await models.Order.get(
        id=order_id
    ).prefetch_related(
        'delivery_point'
    ).prefetch_related('status_set')

    status = await order_obj.current_status.first()
    delivery_point = await order_obj.delivery_point.first()

    assert order_obj.comment == expected['comment']
    assert order_obj.delivery_status['status'] == expected['delivery_status']
    assert status.slug == expected['current_status']
    assert float(delivery_point.latitude) == expected['delivery_point']['latitude']
    assert float(delivery_point.longitude) == expected['delivery_point']['longitude']
    assert delivery_point.address == expected['delivery_point']['address']


@pytest.mark.asyncio
async def test_update_delivery_point_invalid_role(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    request_and_expected,
    update_order_delivery_point,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    request, expected = request_and_expected('invalid_role')
    user_id = request['user_id']
    order_id = request['order_id']
    user_role = request['user_role']
    data = request['data']

    with pytest.raises(exceptions.RoleUnavailable) as excinfo:
        await update_order_delivery_point.init(user_id, order_id, user_role, data)
    assert expected == str(excinfo.value)


@pytest.mark.asyncio
async def test_update_delivery_point_invalid_data_courier(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    request_and_expected,
    update_order_delivery_point,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    request, expected = request_and_expected('invalid_data_courier')
    user_id = request['user_id']
    order_id = request['order_id']
    user_role = request['user_role']
    data = request['data']

    with pytest.raises(exceptions.InvalidBody) as excinfo:
        await update_order_delivery_point.init(user_id, order_id, user_role, data)
    assert expected == str(excinfo.value)


@pytest.mark.asyncio
async def test_update_delivery_point_invalid_data_supervisor(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    request_and_expected,
    update_order_delivery_point,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    request, expected = request_and_expected('invalid_data_courier')
    user_id = request['user_id']
    order_id = request['order_id']
    user_role = request['user_role']
    data = request['data']

    with pytest.raises(exceptions.InvalidBody) as excinfo:
        await update_order_delivery_point.init(user_id, order_id, user_role, data)
    assert expected == str(excinfo.value)


@pytest.mark.asyncio
async def test_update_delivery_point_valid_courier_updated(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    request_and_expected,
    update_order_delivery_point,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    request, expected = request_and_expected('valid_courier_updated')
    user_id = request['user_id']
    order_id = request['order_id']
    user_role = request['user_role']
    data = request['data']

    await update_order_delivery_point.init(user_id, order_id, user_role, data)

    order_obj = await models.Order.get(
        id=order_id
    ).prefetch_related(
        'delivery_point'
    ).prefetch_related('status_set')

    status = await order_obj.current_status.first()
    delivery_point = await order_obj.delivery_point.first()

    assert order_obj.comment == expected['comment']
    assert order_obj.delivery_status['status'] == expected['delivery_status']
    assert status.slug == expected['current_status']
    assert float(delivery_point.latitude) == expected['delivery_point']['latitude']
    assert float(delivery_point.longitude) == expected['delivery_point']['longitude']
    assert delivery_point.address == expected['delivery_point']['address']
