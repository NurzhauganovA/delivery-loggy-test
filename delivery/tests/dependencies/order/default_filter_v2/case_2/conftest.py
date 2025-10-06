import os
from unittest.mock import MagicMock

import pytest

from api.schemas import (
    UserCurrent,
)
from tests.fixtures.default_pre_start_sql_scripts import default_pre_start_sql_script
from tests.utils import get_sql_script_from_fixtures_list


@pytest.fixture
def bank_manager() -> UserCurrent:
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'bank_manager',
            'profile_content': {
                'partner_id': 1,
            }
        }
    )


@pytest.fixture
def branch_manager() -> UserCurrent:
    city = MagicMock()
    city.id = 1
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'branch_manager',
            'profile_content': {
                'partner_id': 1,
                'city_id': 1,
                'cities': [
                    city,
                ],
            }
        }
    )


@pytest.fixture
def call_center_manager() -> UserCurrent:
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'call_center_manager',
            'profile_content': {
                'partner_id': 1,
                'country_id': 1,
            }
        }
    )


@pytest.fixture
def courier() -> UserCurrent:
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'courier',
            'profile_content': {
                'partner_id': 1,
                'city_id': 1,
            }
        }
    )


@pytest.fixture
def dispatcher() -> UserCurrent:
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'dispatcher',
            'profile_content': {
                'partner_id': 1,
            }
        }
    )


@pytest.fixture
def manager() -> UserCurrent:
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'manager',
            'profile_content': {
                'partner_id': 1,
            }
        }
    )


@pytest.fixture
def partner_branch_manager() -> UserCurrent:
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'manager',
            'profile_content': {
                'partner_id': 1,
                'city_id': 1,
            }
        }
    )


@pytest.fixture
def service_manager() -> UserCurrent:
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
                'city_id': 1,
            }
        }
    )


@pytest.fixture
def sorter() -> UserCurrent:
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'sorter',
            'profile_content': {
                'partner_id': 1,
            }
        }
    )


@pytest.fixture
def supervisor() -> UserCurrent:
    return UserCurrent(
        id=1,
        phone_number='+777123112233',
        has_password=True,
        partners=[1, 2, 3],
        profile={
            'id': 1,
            'profile_type': 'supervisor',
            'profile_content': {
                'partner_id': 1,
                'country_id': 1,
            }
        }
    )


@pytest.fixture
async def fixtures() -> list:
    return [
        'user',
        'partner',
        'partner_shipment_point',
        'profile_service_manager',
        'profile_bank_manager',
        'profile_branch_manager',
        'profile_call_center_manager',
        'profile_courier',
        'profile_dispatcher',
        'profile_manager',
        'profile_partner_branch_manager',
        'profile_sorter',
        'profile_supervisor',
        'groups_user',
        'deliverygraph',
        'item',
        'item_city',
        'delivery_point',
        'postcontrol_configs',
        'order',
        'order.statuses',
    ]


@pytest.fixture
def pre_start_sql_script(request, fixtures, default_pre_start_sql_script) -> str:
    current_test_sql_scripts = get_sql_script_from_fixtures_list(
        current_dir=os.path.dirname(str(request.fspath)),
        fixtures=fixtures,
    )

    return default_pre_start_sql_script + current_test_sql_scripts
