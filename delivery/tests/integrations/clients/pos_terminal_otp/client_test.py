import pytest

from api.clients.pos_terminal_otp import PosTerminalOTPClient


@pytest.mark.asyncio
async def test_send_otp(client: PosTerminalOTPClient):
    """Отправка ОТП"""
    response = await client.send(
        business_key='OVERDRAFT-TMS25-02268',
        phone_number="77051234567",
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_send_and_verify_otp(client: PosTerminalOTPClient):
    """Отправка и проверка ОТП"""

    response = await client.send(
        phone_number="+77476911585",
    )
    assert response.status_code == 200

    response = await client.verify(
        business_key='OVERDRAFT-TMS25-02268',
        phone_number="+77476911585",
        otp_code="4672",
        courier_full_name='Кыдырбаева Дана Курбанбаевна',
    )
    assert response.status_code == 200
    assert response.json() == 'SUCCESS'

@pytest.mark.asyncio
async def test_verify_otp_with_no_sending_otp(client: PosTerminalOTPClient):
    """Проверка ОТП без отправки"""
    response = await client.verify(
        business_key='OVERDRAFT-TMS25-02268',
        phone_number="77051234111",
        otp_code="1234",
        courier_full_name='Кыдырбаева Дана Курбанбаевна',
    )
    assert response.status_code == 200
    assert response.json() == 'NOT_FOUND'


@pytest.mark.asyncio
async def test_verify_otp_with_invalid_otp(client: PosTerminalOTPClient):
    """Отправка и проверка ОТП, но ОТП код неверный"""
    response = await client.send(
        business_key='OVERDRAFT-TMS25-02268',
        phone_number="77051234567",
    )
    assert response.status_code == 200

    response = await client.verify(
        business_key='OVERDRAFT-TMS25-02268',
        phone_number="77051234567",
        otp_code="1111",
        courier_full_name='Кыдырбаева Дана Курбанбаевна',
    )
    assert response.status_code == 200
    assert response.json() == 'FAILURE'
