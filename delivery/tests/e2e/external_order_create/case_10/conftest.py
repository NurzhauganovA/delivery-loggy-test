import pytest

from delivery.tests.utils import json_fixture
from delivery.tests.utils import query

from tests.fixtures.default_pre_start_sql_scripts import (
    default_countries_insert_script,
    default_cities_insert_script,
    statuses_insert_script
)


@pytest.fixture
def body() -> dict:
    json = {
            "city": "Алматы",
            "comment": "Нет комментариев",
            "delivery_datetime": "2025-03-13T12:22:00.350Z",
            "item_id": 1,
            "receiver_name": "Имя Фамилия",
            "receiver_phone_number": "+77056119742",
            "type": "planned",
            "callbacks": {
                "set_otp": "https://bankffin.kz/api/set-opt?orderId=1234",
                "set_pan": "https://bankffin.kz/api/set-pan?orderId=1234",
                "set_photo_urls": "https://bankffin.kz/api/set-photo?orderId=1234"
            },
            "address": "Алматы, Жибек Жолы 135",
            "latitude": 43.24796815,
            "longitude": 76.95038633,
            "partner_order_id": "223o486346082346074360368",
            "product_type": "sep_unembossed",
            "product_name": "Доставка неименных карт",
            "payload": {
                "client_code": "001666280"
            }
        }
    return json


@pytest.fixture
def invalid_body() -> dict:
    json = {
            "city": "Алматы",
            "comment": "Нет комментариев",
            "delivery_datetime": "2025-03-13T12:22:00.350Z",
            "item_id": 1,
            "receiver_name": "Имя Фамилия",
            "receiver_iin": "123456789012",
            "receiver_phone_number": "+77056119742",
            "type": "planned",
            "callbacks": {
                "set_otp": "https://bankffin.kz/api/set-opt?orderId=1234",
                "set_pan": "https://bankffin.kz/api/set-pan?orderId=1234",
                "set_photo_urls": "https://bankffin.kz/api/set-photo?orderId=1234"
            },
            "address": "Алматы, Жибек Жолы 135",
            "latitude": 43.24796815,
            "longitude": 76.95038633,
            "partner_order_id": "223o486346082346074360368",
            "product_type": "sep_unembossed",
            "product_name": "Доставка неименных карт",
            "payload": []
        }
    return json


@pytest.fixture
def api_key() -> str:
    return "1111"


@pytest.fixture
def expected() -> str:
    return "001666280"


@pytest.fixture
def pre_start_sql_script() -> str:
    """Важен порядок скриптов, так как есть зависимость от внешних ключей у таблиц"""
    scripts = [
        default_countries_insert_script(),
        default_cities_insert_script(),
        statuses_insert_script(),
    ]
    tables_and_fixtures = {
        'public.partner': 'partner',
        'public."partner.publicapitoken"': 'publicapitoken',
        'public.item': 'item',
        'public.item_city': 'item_city',
        'public.deliverygraph': 'deliverygraph',
        'public.item_deliverygraph': 'item_deliverygraph',
        'public.partner_shipment_point': 'partner_shipment_point',
    }
    for table, fixture in tables_and_fixtures.items():
        fixtures = json_fixture.get_fixture(
            'e2e',
            'external_order_create/case_10',
            fixture,
        )
        insert_query = query.create_insert(table, fixtures)
        scripts.append(insert_query)

    return " ".join(scripts)
