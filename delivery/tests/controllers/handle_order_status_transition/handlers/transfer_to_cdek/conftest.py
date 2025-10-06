import os

import json
import pytest

from _pytest.fixtures import FixtureRequest

from unittest.mock import(
    AsyncMock,
    MagicMock,
)

from tests.conftest import CUR_DIR
from tests.utils import(
    query,
    json_fixture,
)

from tests.fixtures.default_pre_start_sql_scripts import(
    default_pre_start_sql_script,
    get_sql_script_from_fixtures,
)

from api import models
from api.controllers.handle_order_status_transition.handlers import TransferToCDEK


@pytest.fixture
def mock_cdek_adapter():
    cdek_adapter = MagicMock()
    cdek_adapter.order_create = AsyncMock()
    cdek_adapter.return_value = '214876ac-fb04-453d-a1d3-e89b304e4e3e'
    return cdek_adapter


@pytest.fixture
def handler(mock_cdek_adapter: AsyncMock) -> TransferToCDEK:
    return TransferToCDEK(
        cdek_adapter=mock_cdek_adapter,
    )


@pytest.fixture
def valid() -> dict:
    return {
        "order_id": 1,
        "warehouse_id": "12345",
        "latitude": 12.34,
        "longitude": 23.45,
        "address": "Улица Приколиста Дом Юмориста 69"
    }


@pytest.fixture
def invalid() -> dict:
    return {
        "order_id": 2,
        "warehouse_id": "12345",
        "latitude": 12.34,
        "longitude": 23.45,
    }


@pytest.fixture
def expected() -> dict:
    return {
        'track_number': '214876ac-fb04-453d-a1d3-e89b304e4e3e',
        'delivery_status': {
            'status': 'transfer_to_cdek',
            'datetime': None,
            'reason': None,
            'comment': None,
        }

    }

@pytest.fixture
def fixtures() -> dict:
    return {
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
        'courier_service': 'courier_service',
    }


@pytest.fixture
def pre_start_sql_script(
    request: FixtureRequest,
    fixtures: dict,
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

    current_test_sql_scripts = get_sql_script_from_fixtures(
        current_dir=os.path.dirname(str(request.fspath)),
        fixtures=fixtures,
    )

    return default_pre_start_sql_script + current_test_sql_scripts
