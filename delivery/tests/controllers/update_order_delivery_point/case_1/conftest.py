import json
import pytest

from typing import(
    Tuple,
    Union,
    Callable,
)

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
)

from api.controllers.update_order_delivery_point.controller import UpdateOrderDeliveryPoint

from delivery.tests.conftest import CUR_DIR


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

    tables_and_fixtures = {
        'status': 'status',
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
    }
    for table, fixture in tables_and_fixtures.items():
        fixtures = json_fixture.get_fixture(
            'controllers',
            'update_order_delivery_point/case_1',
            fixture,
        )
        insert_query = query.create_insert(table, fixtures)
        scripts.append(insert_query)

    return " ".join(scripts)


@pytest.fixture
def request_and_expected() -> Callable[[str], Tuple[dict, Union[dict, str]]]:
    def _load(fixture_name: str) -> Tuple[dict, Union[dict, str]]:
        if not fixture_name.endswith('.json'):
            fixture_name += '.json'
        path = f'{CUR_DIR}/controllers/update_order_delivery_point/case_1/cases/{fixture_name}'
        with open(path) as file:
            file_data = json.load(file)
        return file_data['request'], file_data['expected']
    return _load


@pytest.fixture
def update_order_delivery_point() -> UpdateOrderDeliveryPoint:
    return UpdateOrderDeliveryPoint()
