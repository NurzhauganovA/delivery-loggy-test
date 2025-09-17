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
        'profile_type': 'service_manager',
        'profile_id': '1',
    }


@pytest.fixture
def expected_history_record() -> dict:
    return {
        'current_page': 1,
        'items': [
            {
                'action_data': {'id': 1, 'text': 'Sample comment text'},
                'created_at': '2025-04-14T17:00:00+00:00',
                'initiator': {
                    'first_name': 'Служба 1',
                    'id': 1,
                    'last_name': 'Службавна 1',
                    'middle_name': 'Службавна 1',
                    'profile_types': ['service_manager']
                },
                'initiator_id': 1,
                'initiator_role': 'service_manager',
                'initiator_type': 'User',
                'model_id': 1,
                'model_type': 'Order',
                'request_method': 'POST'
            }
        ],
        'total': 1,
        'total_pages': 1,
    }

@pytest.fixture
def fixtures()-> dict:
    return {
        'public."user"': 'user',
        'public."partner"': 'partner',
        'public."profile_service_manager"': 'profile_service_manager',
        'public."groups_user"': 'groups_user',
        'public."partner_shipment_point"': 'partner_shipment_point',
        'public."item"': 'item',
        'public."item_city"': 'item_city',
        'public."deliverygraph"': 'deliverygraph',
        'public."item_deliverygraph"': 'item_deliverygraph',
        'public."delivery_point"': 'delivery_point',
        'public."order"': 'order',
    }


@pytest.fixture
def pre_start_sql_script(request, fixtures, default_pre_start_sql_script) -> str:
    current_test_sql_scripts = get_sql_script_from_fixtures(
        current_dir=os.path.dirname(str(request.fspath)),
        fixtures=fixtures,
    )

    return default_pre_start_sql_script + current_test_sql_scripts
