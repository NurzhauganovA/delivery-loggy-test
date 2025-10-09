import os

import pytest

from tests.fixtures.default_pre_start_sql_scripts import default_pre_start_sql_script
from tests.utils import get_sql_script_from_fixtures


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
        'profile_type': 'logist',
        'profile_id': '1',
    }

@pytest.fixture
def expected() -> dict:
    return {
        "statuses": [
            {
                'status': {
                    'name': 'New order',
                    'is_optional': False,
                    'icon': 'order_new',
                    'partner_id': None,
                    'after': None,
                    'id': 1,
                    'slug': 'novaia-zaiavka'
                },
                'created_at': '2024-02-08T06:11:17.160374+00:00'
            },
            {
                'status': {
                    'name': 'Transfer to CDEK',
                    'is_optional': False,
                    'icon': 'transfer_to_cdek',
                    'partner_id': None,
                    'after': None,
                    'id': 37,
                    'slug': 'transfer_to_cdek'
                },
                'created_at': '2024-02-08T09:11:17.160374+00:00',
                'sub_statuses': [
                    {
                        'name': 'Создан',
                        'created_at': '2024-02-08T09:00:00+00:00'
                    },
                    {
                        'name': 'Удален',
                        'created_at': '2024-02-08T09:01:00+00:00'
                    },
                    {
                        'name': 'Принят на склад отправителя',
                        'created_at': '2024-02-08T09:02:00+00:00'
                    }
                ]
            }
        ]
    }



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
        'public."profile_logist"': 'profile_logist',
        'public."profile_courier"': 'profile_courier',
        'public."profile_courier_area"': 'profile_courier_area',
        'public."order"': 'order',
        'public."postcontrol_configs"': 'postcontrol_configs',
        'public."order.postcontrols"': 'order.postcontrols',
        'public."order_comment"': 'order_comment',
        'public."order_comment_image"': 'order_comment_image',
        'public."order.statuses"': 'order.statuses',
        'public."courier_service_status"': 'courier_service_status',
    }


@pytest.fixture
def pre_start_sql_script(request, fixtures, default_pre_start_sql_script) -> str:
    current_test_sql_scripts = get_sql_script_from_fixtures(
        current_dir=os.path.dirname(str(request.fspath)),
        fixtures=fixtures,
    )

    return default_pre_start_sql_script + current_test_sql_scripts
