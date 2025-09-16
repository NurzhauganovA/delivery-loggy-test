from unittest.mock import Mock

import pytest

from api.schemas import SaveCourierGeolocation, UserCurrent
from tests.fixtures.default_pre_start_sql_scripts import (
    default_groups_insert_script,
    default_permissions_insert_script,
    default_groups_permissions_insert_script,
    default_countries_insert_script,
    default_cities_insert_script,
    statuses_insert_script
)
from tests.utils import json_fixture, query

@pytest.fixture
def data() -> SaveCourierGeolocation:
    return SaveCourierGeolocation(
        latitude=123.123,
        longitude=456.456,
        order_id=1,
    )

@pytest.fixture
def courier() -> UserCurrent:
    return Mock(
        id=1,
        profile={'profile_type': 'courier'}
    )


@pytest.fixture
def pre_start_sql_script() -> str:
    """Важен порядок скриптов, так как есть зависимость от внешних ключей у таблиц"""
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
        'public."partner"': 'partner',
        'public."profile_service_manager"': 'profile_service_manager',
        'public."groups_user"': 'groups_user',
        'public."item"': 'item',
        'public."item_city"': 'item_city',
        'public."deliverygraph"': 'deliverygraph',
        'public."delivery_point"': 'delivery_point',
        'public."area"': 'area',
        'public."profile_courier"': 'profile_courier',
        'public."profile_courier_area"': 'profile_courier_area',
        'public."order"': 'order',
        'public."order.statuses"': 'order.statuses',
    }

    for table, fixture in tables_and_fixtures.items():
        fixtures = json_fixture.get_fixture(
            'e2e',
            'save_courier_geolocation',
            fixture,
        )
        insert_query = query.create_insert(table, fixtures)
        scripts.append(insert_query)

    return " ".join(scripts)
