import uuid

import pytest
from api.clients.freedom_bank_otp import FreedomBankOTPClient


@pytest.mark.skip(reason="Интеграционный тест")
@pytest.mark.asyncio
async def test_send_otp(client: FreedomBankOTPClient):
    """Отправка ОТП"""
    response = await client.send(
        request_id="BFF000042",
    )
    assert response.status_code == 202


@pytest.mark.skip(reason="Интеграционный тест")
@pytest.mark.asyncio
async def test_send_and_verify_otp(client: FreedomBankOTPClient):
    """Отправка и проверка ОТП"""
    request_id = "BFF000042"

    response = await client.send(
        request_id=request_id,
    )
    assert response.status_code == 202

    response = await client.verify(
        otp_code="1234",
        request_id=request_id,
    )
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "errorCode": None,
        "errorMessage": None,
        "payload": "SUCCESS"
    }

@pytest.mark.skip(reason="Интеграционный тест. При реальном вызове не проверить кейс")
@pytest.mark.asyncio
async def test_verify_otp_with_no_sending_otp(client: FreedomBankOTPClient):
    """Проверка ОТП без отправки"""
    response = await client.verify(
        otp_code="1234",
        request_id="BFF000042",
    )
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "errorCode": None,
        "errorMessage": None,
        "payload": "NOT_FOUND"
    }

@pytest.mark.skip(reason="Интеграционный тест. При реальном вызове не проверить кейс")
@pytest.mark.asyncio
async def test_verify_otp_with_wrong_request_id(client: FreedomBankOTPClient):
    """Отправка и проверка ОТП, но с разными request_id"""
    response = await client.send(
        request_id="BFF000042",
    )
    assert response.status_code == 202

    response = await client.verify(
        otp_code="1234",
        request_id="BFF000042",
    )
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "errorCode": None,
        "errorMessage": None,
        "payload": "NOT_FOUND"
    }

@pytest.mark.skip(reason="Интеграционный тест")
@pytest.mark.asyncio
async def test_verify_otp_with_wrong_otp(client: FreedomBankOTPClient):
    """Отправка и проверка ОТП, но ОТП код неверный"""
    request_id = "BFF000042"

    response = await client.send(
        request_id=request_id,
    )
    assert response.status_code == 202

    response = await client.verify(
        otp_code="1111",
        request_id=request_id,
    )
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "errorCode": None,
        "errorMessage": None,
        "payload": "FAILURE"
    }
