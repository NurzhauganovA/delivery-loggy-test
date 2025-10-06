import os

import json
import pytest
from _pytest.fixtures import FixtureRequest

from unittest.mock import(
    AsyncMock,
    MagicMock,
)

from tests.utils import(
    query,
    json_fixture,
    get_sql_script_from_fixtures,
)

from tests.fixtures.default_pre_start_sql_scripts import default_pre_start_sql_script



@pytest.fixture
def mock_value():
    mock = AsyncMock(return_value='214876ac-fb04-453d-a1d3-e89b304e4e3e')
    return mock


@pytest.fixture
def path(request: FixtureRequest) -> str:
    return str(request.fspath)


@pytest.fixture
def api_key() -> str:
    return "1111"


@pytest.fixture
def body() -> str:
    json = """
        {
            "city": "Москва",
            "comment": "sample comment",
            "delivery_datetime": "2025-03-13T12:22:00.350Z",
            "item_id": 1,
            "shipment_point_id": 1,
            "receiver_name": "Нурсултан Кемелович",
            "receiver_phone_number": "+77071112233",
            "receiver_iin": "012345050101",
            "type": "planned",
            "callbacks": {
                "set_otp": "https://bankffin.kz/api/set-opt?orderId=1234",
                "set_pan": "https://bankffin.kz/api/set-pan?orderId=1234",
                "set_photo_urls": "https://bankffin.kz/api/set-photo?orderId=1234"
            },
            "address": "Алматы, Жибек Жолы 135",
            "latitude": 72.12332,
            "longitude": 41.232355,
            "partner_order_id": "223o486346082346074360349",

            "product_type": "group_of_cards",
            "product_name": "Групповая доставка ЗП карт",

            "payload": [
                {
                  "id": 0,
                  "pan": "5269xxxxxxxx1234",
                  "iin": "990208350377",
                  "fio": "Иванов Иван"
                },
                {
                  "id": 1,
                  "pan": "5269xxxxxxxx1234",
                  "iin": "990208350377",
                  "fio": "Иванов Иван"
                },
                {
                  "id": 2,
                  "pan": "5269xxxxxxxx1234",
                  "iin": "990208350377",
                  "fio": "Иванов Иван"
                }
            ]
        }
    """
    return json


@pytest.fixture
def expected() -> dict:
    response = {
        'current_status': 'transfer_to_cdek',
        'courier_service': 'cdek',
        'delivery_status': {
            'status': 'transfer_to_cdek',
            'datetime': None,
            'reason': None,
            'comment': None,
        }
    }
    return response


@pytest.fixture
def fixtures() -> dict:
    return {
        'public."user"': 'user',
        'partner': 'partner',
        'public."partner.publicapitoken"': 'partner_publicapitoken',
        'partner_shipment_point': 'partner_shipment_point',
        'public.profile_courier': 'profile_courier',
        'item': 'item',
        'item_city': 'item_city',
        'deliverygraph': 'deliverygraph',
        'item_deliverygraph': 'item_deliverygraph',
        'public.area': 'area',
        'public."order"': 'order',
        'public."order.statuses"': 'order_statuses',
        'product': 'product',
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
