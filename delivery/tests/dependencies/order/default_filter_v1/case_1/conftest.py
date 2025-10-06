import os

import pytest

from api.schemas import (
    UserCurrent,
)
from tests.fixtures.default_pre_start_sql_scripts import default_pre_start_sql_script
from tests.utils import get_sql_script_from_fixtures, get_sql_script_from_fixtures_list


@pytest.fixture
async def service_manager():
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'service_manager',
            'profile_content': {
                'partner_id': 1,
            }
        }
    )


@pytest.fixture
async def logist():
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'logist',
            'profile_content': {
                'partner_id': 1,
                'country_id': 1,
            }
        }
    )


@pytest.fixture
async def support():
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'support',
            'profile_content': {
                'partner_id': 1,
            }
        }
    )


@pytest.fixture
async def general_ccm():
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'general_call_center_manager',
            'profile_content': {
                'partner_id': 1,
            }
        }
    )


@pytest.fixture
def fixtures() -> list:
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
