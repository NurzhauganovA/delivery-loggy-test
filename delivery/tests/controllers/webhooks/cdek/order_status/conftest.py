import os

import pytest

from tests.fixtures.default_pre_start_sql_scripts import default_pre_start_sql_script
from tests.utils import get_sql_script_from_fixtures


@pytest.fixture
def body() -> str:
    json = """
        {
            "type": "ORDER_STATUS",
            "date_time": "2023-11-28T07:44:45+0000",
            "uuid": "72753031-1820-4f99-9240-aab139f05ca5",
            "attributes": {
                "is_return": false,
                "is_reverse": false,
                "is_client_return": false,
                "cdek_number": "1100285492",
                "number": "17011574744791",
                "related_entities": [],
                "code": "RECEIVED_AT_SHIPMENT_WAREHOUSE",
                "status_code": "3",
                "status_date_time": "2023-11-28T07:44:45+0000",
                "city_name": "Новосибирск",
                "city_code": "270"
            }
        }
    """
    return json



@pytest.fixture
def api_key() -> str:
    return "12345"


@pytest.fixture
def fixtures()-> dict:
    return {
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
        'public."postcontrol_configs"': 'postcontrol_configs',
        'public."order.postcontrols"': 'order.postcontrols',
        'public."order_comment"': 'order_comment',
        'public."order_comment_image"': 'order_comment_image',
        'public."order.statuses"': 'order.statuses',
    }


@pytest.fixture
def pre_start_sql_script(request, fixtures, default_pre_start_sql_script) -> str:
    current_test_sql_scripts = get_sql_script_from_fixtures(
        current_dir=os.path.dirname(str(request.fspath)),
        fixtures=fixtures,
    )

    return default_pre_start_sql_script + current_test_sql_scripts
