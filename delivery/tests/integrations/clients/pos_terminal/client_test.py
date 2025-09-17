import pytest

from api.clients.pos_terminal import POSTerminalClient


@pytest.mark.skip(reason="Интеграционный тест")
@pytest.mark.asyncio
async def test_registrate_pos_terminal(client: POSTerminalClient):
    """Отправка ОТП"""
    response = await client.registrate_pos_terminal(
        serial_number="284053989234955843",
        model="PAX",
        merchant_id="60013636",
        terminal_id="80007875",
        receiver_iin="020718601400",
        store_name="Alatau centre",
        store_address="Alatau centre",
        branch_name="0",
        oked_code="",
        mcc_code="",
        receiver_phone_number="+77476911585",
        receiver_full_name="Кыдырбаева Дана Курбанбаевна",
        courier_full_name="Тестовый Курьер Курьерович",
        request_number_ref=None,
        is_installment_enabled=False,
        inventory_number=None,
        sum=0.0,
    )
    assert response.status_code == 200

    data = response.json()
    assert data.get("id")
    assert data.get("businessKey")
