import pytest

from api.schemas.order_payload import POSTerminalPayload


async def test_pos_terminal_payload_schema():
    validator = POSTerminalPayload(
        company_name='some_company_name',
        merchant_id='some_merchant_id',
        terminal_id='some_terminal_id',
        branch_name='some_branch_name',
        mcc_code='code',
        oked_code='some_oked_code',
        oked_text='some_oked_text',
        model='PAX',
        serial_number='12345',
        inventory_number='123456789',
        sum='12345678.1000',
    )
    assert validator.json() == (
        '{"is_installment_enabled": false, "is_installment_limit": false, "model": '
        '"PAX", "serial_number": "12345", "company_name": "some_company_name", '
        '"merchant_id": "some_merchant_id", "terminal_id": "some_terminal_id", '
        '"store_name": null, "branch_name": "some_branch_name", "mcc_code": "code", '
        '"oked_code": "some_oked_code", "oked_text": "some_oked_text", '
        '"request_number_ref": null, "inventory_number": "123456789", "sum": '
        '12345678.1}'
    )


async def test_pos_terminal_payload_schema_with_invalid_sum():
    with pytest.raises(ValueError, match='sum is too large'):
        POSTerminalPayload(
            company_name='some_company_name',
            merchant_id='some_merchant_id',
            terminal_id='some_terminal_id',
            branch_name='some_branch_name',
            mcc_code='code',
            oked_code='some_oked_code',
            oked_text='some_oked_text',
            model='PAX',
            serial_number='12345',
            inventory_number='123456789',
            sum='12345678910.1',
        )
