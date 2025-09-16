import json
import pytest

from tests.utils import(
    query,
    json_fixture,
)

from tests.fixtures.default_pre_start_sql_scripts import (
    default_countries_insert_script,
    default_cities_insert_script,
    statuses_insert_script,
    default_groups_insert_script,
    default_permissions_insert_script,
    default_groups_permissions_insert_script,
)


@pytest.fixture
def credentials() -> dict[str, str]:
    return {
        'grant_type': 'password',
        'username': '+77777777777',
        'password': 'test'
    }


@pytest.fixture
def profile_data() -> dict[str, str]:
    return {
        'profile_type': 'courier',
        'profile_id': '1',
    }


@pytest.fixture
def order_new_delivery_point() -> str:
    json = """
         {
            "delivery_point": {
                "latitude": 12.345678,
                "longitude": 12.345678,
                "address": "Улица Пианиста, Дом Колбасиста 7"
            },
            "comment": "Космос подсказал что клиент находится тут"
        }
    """
    return json


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
        'groups_user': 'groups_user',
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
            'e2e',
            'update_order_delivery_point/case_1',
            fixture,
        )
        insert_query = query.create_insert(table, fixtures)
        scripts.append(insert_query)

    return " ".join(scripts)
