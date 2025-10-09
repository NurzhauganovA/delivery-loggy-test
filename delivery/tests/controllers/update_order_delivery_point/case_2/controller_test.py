from decimal import Decimal

import pytest

from api import models
from tests.fixtures.database import (
    db,
    run_pre_start_sql_script,
)


@pytest.mark.asyncio
async def test_update_delivery_point_within_same_area_by_courier(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    update_order_delivery_point,
):
    """
    Anything except delivery point must be kept untouched
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    user_id = 1
    order_id = 1
    user_role = 'courier'
    data = {
        'delivery_point': {
            'latitude': 76.93244936171875,
            'longitude': 43.24643173612828,
            'address': 'Test delivery point',
        },
        'comment': 'Something important',
    }

    await update_order_delivery_point.init(user_id, order_id, user_role, data)

    order_obj = await models.Order.get(
        id=order_id
    ).prefetch_related(
        'delivery_point'
    ).prefetch_related('status_set')

    status = await order_obj.current_status.first()
    delivery_point = await order_obj.delivery_point.first()

    assert order_obj.courier_id == 1
    assert order_obj.city_id == 1
    assert order_obj.comment == 'Something important'
    assert order_obj.delivery_status['status'] == 'on-the-way-to-call-point'
    assert status.slug == 'kurer-naznachen'
    assert delivery_point.latitude == Decimal('76.93244936')
    assert delivery_point.longitude == Decimal('43.24643174')
    assert delivery_point.address == 'Test delivery point'


@pytest.mark.asyncio
async def test_update_delivery_point_within_same_area_by_supervisor(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    update_order_delivery_point,
):
    """
    Despite new delivery point located in the same delivery area,
    courier must be unlinked from the order.
    delivery status changes to 'address_changed'
    and statuses must be cleared and 'novaia-zaiavka' added again.
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    user_id = 1
    order_id = 1
    user_role = 'supervisor'
    data = {
        'delivery_point': {
            'latitude': 76.93244936171875,
            'longitude': 43.24643173612828,
            'address': 'Test delivery point',
        },
        'comment': 'Something important',
    }

    await update_order_delivery_point.init(user_id, order_id, user_role, data)

    order_obj = await models.Order.get(
        id=order_id
    ).prefetch_related(
        'delivery_point'
    ).prefetch_related('status_set')

    status = await order_obj.current_status.first()
    delivery_point = await order_obj.delivery_point.first()

    assert order_obj.courier_id is None
    assert order_obj.city_id == 1
    assert order_obj.comment == 'Something important'
    assert order_obj.delivery_status['status'] == 'address_changed'
    assert status.slug == 'novaia-zaiavka'
    assert delivery_point.latitude == Decimal('76.93244936')
    assert delivery_point.longitude == Decimal('43.24643174')
    assert delivery_point.address == 'Test delivery point'


@pytest.mark.asyncio
async def test_update_delivery_point_within_different_area_by_courier(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    update_order_delivery_point,
):
    """
    Delivery point located in the different delivery area,
    courier must be unlinked from the order.
    delivery status changes to 'address_changed'
    and statuses must be cleared and 'novaia-zaiavka' added again.
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    user_id = 1
    order_id = 1
    user_role = 'courier'
    data = {
        'delivery_point': {
            'latitude': 76.97602671,
            'longitude': 43.31921254,
            'address': 'Test delivery point',
        },
        'comment': 'Something important',
    }

    await update_order_delivery_point.init(user_id, order_id, user_role, data)

    order_obj = await models.Order.get(
        id=order_id
    ).prefetch_related(
        'delivery_point'
    ).prefetch_related('status_set')

    status = await order_obj.current_status.first()
    delivery_point = await order_obj.delivery_point.first()

    assert order_obj.courier_id is None
    assert order_obj.city_id == 1
    assert order_obj.comment == 'Something important'
    assert order_obj.delivery_status['status'] == 'address_changed'
    assert status.slug == 'novaia-zaiavka'
    assert delivery_point.latitude == Decimal('76.97602671')
    assert delivery_point.longitude == Decimal('43.31921254')
    assert delivery_point.address == 'Test delivery point'


@pytest.mark.asyncio
async def test_update_delivery_point_on_different_city_by_courier(
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    update_order_delivery_point,
):
    """
    Delivery point on different city,
    courier must be unlinked from the order.
    delivery status changes to 'address_changed'
    and statuses must be cleared and 'novaia-zaiavka' added again.
    City changes to passed value
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    user_id = 1
    order_id = 1
    user_role = 'courier'
    data = {
        'delivery_point': {
            'latitude': 71.43222717,
            'longitude': 51.18043911,
            'address': 'Test delivery point',
        },
        'city_id': 2,
        'comment': 'Something important',
    }

    await update_order_delivery_point.init(user_id, order_id, user_role, data)

    order_obj = await models.Order.get(
        id=order_id
    ).prefetch_related(
        'delivery_point'
    ).prefetch_related('status_set')

    status = await order_obj.current_status.first()
    delivery_point = await order_obj.delivery_point.first()

    assert order_obj.courier_id is None
    assert order_obj.city_id == 2
    assert order_obj.comment == 'Something important'
    assert order_obj.delivery_status['status'] == 'address_changed'
    assert status.slug == 'novaia-zaiavka'
    assert delivery_point.latitude == Decimal('71.43222717')
    assert delivery_point.longitude == Decimal('51.18043911')
    assert delivery_point.address == 'Test delivery point'
