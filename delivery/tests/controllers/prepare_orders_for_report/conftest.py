import pytest

from tests.utils import(
    query,
    json_fixture,
)

from tests.fixtures.default_pre_start_sql_scripts import (
    default_groups_insert_script,
    default_permissions_insert_script,
    default_groups_permissions_insert_script,
    default_countries_insert_script,
    default_cities_insert_script,
    statuses_insert_script,
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
        statuses_insert_script(),
    ]

    tables_and_fixtures = {
        'public."user"': 'user',
        'partner': 'partner',
        'public.profile_courier': 'profile_courier',
        'item': 'item',
        'public.area': 'area',
        'deliverygraph': 'delivery_graph',
        'public.delivery_point': 'delivery_point',
        'public."order"': 'order',
        'public."order.statuses"': 'order_statuses',
        'product': 'product',
        'history': 'history',
    }
    for table, fixture in tables_and_fixtures.items():
        fixtures = json_fixture.get_fixture(
            'controllers',
            'prepare_orders_for_report',
            fixture,
        )
        insert_query = query.create_insert(table, fixtures)
        scripts.append(insert_query)

    return " ".join(scripts)
