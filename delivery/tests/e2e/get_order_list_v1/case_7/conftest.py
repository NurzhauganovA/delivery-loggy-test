import os

import pytest

from tests.fixtures.default_pre_start_sql_scripts import default_pre_start_sql_script
from tests.utils import get_sql_script_from_fixtures_list


@pytest.fixture
def credentials() -> dict[str, str]:
    return {
        'grant_type': 'password',
        'username': '+77777777777',
        'password': 'test'
    }


@pytest.fixture
def profile_logist() -> dict[str, str]:
    return {
        'profile_type': 'logist',
        'profile_id': '1',
    }


@pytest.fixture
def profile_support() -> dict[str, str]:
    return {
        'profile_type': 'support',
        'profile_id': '1',
    }


@pytest.fixture
def profile_general_call_center_manager() -> dict[str, str]:
    return {
        'profile_type': 'general_call_center_manager',
        'profile_id': '1',
    }


@pytest.fixture
def fixtures()-> list:
    return [
        'user',
        'partner',
        'profile_service_manager',
        'profile_logist',
        'profile_support',
        'profile_general_call_center_manager',
        'groups_user',
        'item',
        'item_city',
        'deliverygraph',
        'delivery_point',
        'area',
        'profile_courier',
        'profile_courier_area',
        'order',
        'postcontrol_configs',
        'order.postcontrols',
        'order.statuses',
    ]


@pytest.fixture
def pre_start_sql_script(request, fixtures, default_pre_start_sql_script) -> str:
    current_test_sql_scripts = get_sql_script_from_fixtures_list(
        current_dir=os.path.dirname(str(request.fspath)),
        fixtures=fixtures,
    )

    return default_pre_start_sql_script + current_test_sql_scripts
