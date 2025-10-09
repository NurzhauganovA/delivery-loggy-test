import pytest

from api.schemas.order_payload import POSTerminalPayload


async def test_pos_terminal_payload_schema():
    schema = POSTerminalPayload(
        company_name='some_company_name',
        merchant_id='some_merchant_id',
        terminal_id='some_terminal_id',
        branch_name='some_branch_name',
        mcc_code='code',
        oked_code='some_oked_code',
        oked_text='some_oked_text',
        model='PAX',
        serial_number='12345',
    )
    assert schema.dict() == {'is_installment_enabled': False, 'is_installment_limit': False, 'company_name': 'some_company_name', 'merchant_id': 'some_merchant_id', 'terminal_id': 'some_terminal_id', 'store_name': None, 'branch_name': 'some_branch_name', 'mcc_code': 'code', 'oked_code': 'some_oked_code', 'oked_text': 'some_oked_text', 'request_number_ref': None, 'pan': None}
