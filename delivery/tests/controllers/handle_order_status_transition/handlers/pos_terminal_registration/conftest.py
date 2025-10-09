import os
from decimal import Decimal
from typing import Optional

import pytest

from api.adapters.pos_terminal.exceptions import BasePOSTerminalAdapterError
from api.controllers.handle_order_status_transition.handlers.pos_terminal_registration import POSTerminalRegistrationHandler
from api.controllers.handle_order_status_transition.handlers.pos_terminal_registration.protocols import POSTerminalAdapterProtocol
from tests.fixtures.default_pre_start_sql_scripts import default_pre_start_sql_script
from tests.utils import get_sql_script_from_fixtures


@pytest.fixture
def adapter() -> POSTerminalAdapterProtocol:
    class MockClient:
        async def registrate_pos_terminal(
                self,
                serial_number: str,
                model: str,
                merchant_id: str,
                terminal_id: str,
                receiver_iin: str,
                store_name: str,
                store_address: str,
                branch_name: str,
                oked_code: str,
                mcc_code: str,
                receiver_phone_number: str,
                receiver_full_name: str,
                courier_full_name: str,
                is_installment_enabled: bool,
                request_number_ref: Optional[str],
        ) -> str:
            if serial_number == "77777":
                raise BasePOSTerminalAdapterError()

            return "OVERDRAFT-TMS25-02339"

    return MockClient()


@pytest.fixture
def handler(adapter) -> POSTerminalRegistrationHandler:
    return POSTerminalRegistrationHandler(adapter)


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
        'product': 'product',
    }


@pytest.fixture
def pre_start_sql_script(request, fixtures, default_pre_start_sql_script) -> str:
    current_test_sql_scripts = get_sql_script_from_fixtures(
        current_dir=os.path.dirname(str(request.fspath)),
        fixtures=fixtures,
    )

    return default_pre_start_sql_script + current_test_sql_scripts
