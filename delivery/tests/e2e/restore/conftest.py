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
def expected_pos_terminal_product() -> dict:
    return {
        'attributes': {
            'branch_name': '500000',
            'company_name': 'Mariam',
            'is_installment_enabled': False,
            'is_installment_limit': False,
            'mcc_code': '7299',
            'merchant_id': '70007031',
            'oked_code': '96090',
            'oked_text': 'Предоставление прочих индивидуальных услуг, не '
                         'включенных в другие группировки',
            'pan': '4003********2771',
            'request_number_ref': 'OVERDRAFT25-03927',
            'store_name': 'Mariam',
            'terminal_id': '55000031'
        },
        'id': 2,
        'name': 'Какой то пос терминал',
        'type': 'pos_terminal'
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
        'public."profile_courier"': 'profile_courier',
        'public."profile_courier_area"': 'profile_courier_area',
        'public."order"': 'order',
        'public."order.statuses"': 'order.statuses',
        'public."product"': 'product',
    }


@pytest.fixture
def pre_start_sql_script(request, fixtures, default_pre_start_sql_script) -> str:
    current_test_sql_scripts = get_sql_script_from_fixtures(
        current_dir=os.path.dirname(str(request.fspath)),
        fixtures=fixtures,
    )

    return default_pre_start_sql_script + current_test_sql_scripts
