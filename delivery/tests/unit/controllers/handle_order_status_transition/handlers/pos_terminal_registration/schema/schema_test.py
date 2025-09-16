import pytest

from api.controllers.handle_order_status_transition.handlers.pos_terminal_registration.schema import (
    POSTerminalRegistrationData,
)


async def test_pos_terminal_registration_schema():
    validator = POSTerminalRegistrationData(
        model='PAX',
        serial_number='12345',
        inventory_number='123456789',
        sum='12345678.1000',
    )
    assert validator.json() == '{"model": "PAX", "serial_number": "12345", "inventory_number": "123456789", "sum": 12345678.1}'


async def test_pos_terminal_registration_schema_with_invalid_sum():
    with pytest.raises(ValueError):
        POSTerminalRegistrationData(
            model='PAX',
            serial_number='12345',
            inventory_number='123456789',
            sum='12345678910.1',
        )
