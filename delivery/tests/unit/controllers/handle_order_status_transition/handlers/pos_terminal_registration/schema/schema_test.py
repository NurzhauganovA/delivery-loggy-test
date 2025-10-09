import pytest

from api.controllers.handle_order_status_transition.handlers.pos_terminal_registration.schema import (
    POSTerminalRegistrationData,
)


async def test_pos_terminal_registration_schema():
    schema = POSTerminalRegistrationData(
        model='PAX',
        serial_number='12345',
    )
    assert schema.dict() == {"model": "PAX", "serial_number": "12345"}
