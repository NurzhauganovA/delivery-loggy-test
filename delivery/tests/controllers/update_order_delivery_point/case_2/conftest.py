import pytest

from api.controllers.update_order_delivery_point.controller import UpdateOrderDeliveryPoint
from tests.fixtures.default_pre_start_sql_scripts import (
    default_groups_insert_script,
    default_permissions_insert_script,
    default_groups_permissions_insert_script,
    default_countries_insert_script,
    default_cities_insert_script,
)
from tests.utils import (
    query,
    json_fixture,
)


@pytest.fixture
def pre_start_sql_script() -> str:
    """Важен порядок скриптов,
            так как есть зависимость от внешних ключей у таблиц"""
    scripts = [
        default_groups_insert_script(),
        default_permissions_insert_script(),
        default_groups_permissions_insert_script(),
        default_countries_insert_script(),
        default_cities_insert_script(),
    ]

    tables_and_fixtures = (
        'status',
        'user',
        'partner',
        'profile_courier',
        'item',
        'area',
        'deliverygraph',
        'delivery_point',
        'order',
        'order.statuses',
        'product',
    )
    for fixture in tables_and_fixtures:
        fixtures = json_fixture.get_fixture(
            'controllers',
            'update_order_delivery_point/case_2',
            fixture,
        )
        insert_query = query.create_insert(f'public."{fixture}"', fixtures)
        scripts.append(insert_query)

    return " ".join(scripts)


@pytest.fixture
def update_order_delivery_point() -> UpdateOrderDeliveryPoint:
    return UpdateOrderDeliveryPoint()
