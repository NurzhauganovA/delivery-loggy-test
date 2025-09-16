from decimal import Decimal

import pytest

from api.adapters.pos_terminal import POSTerminalAdapter
from api.adapters.pos_terminal.exceptions import (
    POSTerminalAdapterValidationError,
    POSTerminalAdapterBadRequestError,
)


@pytest.mark.asyncio
async def test_registrate_pos_terminal(adapter: POSTerminalAdapter):
    business_key = await adapter.registrate_pos_terminal(
        serial_number="284053989234955843",
        model="PAX",
        merchant_id="60013636",
        terminal_id="80007875",
        receiver_iin="020718601400",
        store_name="Alatau centre",
        store_address="Alatau centre",
        branch_name="200000",
        oked_code="QWERTY123",
        mcc_code="GGG1",
        receiver_phone_number="+77476911585",
        receiver_full_name="Кыдырбаева Дана Курбанбаевна",
        courier_full_name="Тестовый Курьер Курьерович",
        is_installment_enabled=False,
        request_number_ref=None,
        inventory_number='123456789',
        sum=Decimal('1000.1'),
    )

    assert business_key == "OVERDRAFT-TMS25-02263"


@pytest.mark.asyncio
async def test_registrate_pos_terminal_validation_error(adapter: POSTerminalAdapter):
    with pytest.raises(POSTerminalAdapterValidationError):
        await adapter.registrate_pos_terminal(
            serial_number="",
            model="",
            merchant_id="",
            terminal_id="",
            receiver_iin="",
            store_name="",
            store_address="",
            branch_name="",
            oked_code="",
            mcc_code="",
            receiver_phone_number="",
            receiver_full_name="",
            courier_full_name="",
            is_installment_enabled=False,
            request_number_ref="",
            inventory_number='',
            sum=Decimal('12345678910.11'),
        )


@pytest.mark.asyncio
async def test_registrate_pos_terminal_bad_request_error(adapter: POSTerminalAdapter):
    with pytest.raises(POSTerminalAdapterBadRequestError, match="can not registrate pos terminal, bad request"):
         await adapter.registrate_pos_terminal(
            serial_number="222",
            model="PAX",
            merchant_id="60013636",
            terminal_id="80007875",
            receiver_iin="020718601400",
            store_name="Alatau centre",
            store_address="Alatau centre",
            branch_name="200000",
            oked_code="QWERTY123",
            mcc_code="GGG1",
            receiver_phone_number="+77476911585",
            receiver_full_name="Кыдырбаева Дана Курбанбаевна",
            courier_full_name="Тестовый Курьер Курьерович",
            is_installment_enabled=False,
            request_number_ref=None,
            inventory_number='12345678910',
            sum=Decimal('12345678910.11'),
        )
