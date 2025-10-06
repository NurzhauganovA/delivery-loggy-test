import os

import pytest
from _pytest.fixtures import FixtureRequest

from tests.fixtures.default_pre_start_sql_scripts import (
    default_pre_start_sql_script,
)
from tests.utils import get_sql_script_from_fixtures_list


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
        'profile_type': 'service_manager',
        'profile_id': '1',
    }


@pytest.fixture
def fixtures()-> list:
    return [
        'user',
        'partner',
        'profile_service_manager',
        'groups_user',
        'item',
        'deliverygraph',
        'delivery_point',
        'order',
        'postcontrol_configs',
    ]


@pytest.fixture
def pre_start_sql_script(
    request: FixtureRequest,
    fixtures: list,
    default_pre_start_sql_script: str,
) -> str:
    """
    Сборка всех SQL запросов из json
    Склеивание с устаревшими запросами, для совместимости

    Args:
        request: глобальный объект Pytest
        fixtures: список фикстур. Парсится из словаря выше
        default_pre_start_sql_script: легаси sql запросы

    Returns:
        SQL запрос спарсенный из фикстур
    """

    current_test_sql_scripts = get_sql_script_from_fixtures_list(
        current_dir=os.path.dirname(str(request.fspath)),
        fixtures=fixtures,
    )

    return default_pre_start_sql_script + current_test_sql_scripts
