import pytest

from api.adapters.freedom_bank_otp import (
    FreedomBankOTPAdapter,
    OTPValidationError,
    OTPBadRequestError,
    OTPWrongOTPCode,
)


@pytest.mark.asyncio
async def test_send(adapter: FreedomBankOTPAdapter):
    """
        Ошибки быть не должно, send вернет None
    """
    await adapter.send(
        partner_order_id="BFF000056"
    )


@pytest.mark.asyncio
async def test_send_and_verify(adapter: FreedomBankOTPAdapter):
    """
        Ошибки быть не должно
    """
    await adapter.send(
        partner_order_id="BFF000056"
    )

    await adapter.verify(
        partner_order_id="BFF000056",
        otp_code="1234",
    )


@pytest.mark.asyncio
async def test_send_bad_request(adapter: FreedomBankOTPAdapter):
    """
        Ошибка HTTP с кодом 500, возвращаем ошибку адаптера
    """
    with pytest.raises(OTPBadRequestError, match="can not send otp, bad request"):
        await adapter.send(
            partner_order_id="BFF000500",
        )


@pytest.mark.asyncio
async def test_send_without_partner_order_id(adapter: FreedomBankOTPAdapter):
    """
        Ошибка валидации, нет partner_order_id
    """
    with pytest.raises(OTPValidationError, match="partner_order_id is required"):
        await adapter.send(
            partner_order_id=""
        )


@pytest.mark.asyncio
async def test_verify_bad_request(adapter: FreedomBankOTPAdapter):
    """
        Ошибка HTTP с кодом 500, возвращаем ошибку адаптера
    """
    with pytest.raises(OTPBadRequestError, match="can not verify otp, bad request"):
        await adapter.verify(
            partner_order_id="BFF00500",
            otp_code="2222",
        )


@pytest.mark.asyncio
async def test_verify_without_partner_order_id(adapter: FreedomBankOTPAdapter):
    """
        Ошибка валидации, нет partner_order_id
    """
    with pytest.raises(OTPValidationError, match="partner_order_id is required"):
        await adapter.verify(
            partner_order_id="",
            otp_code="1234",
        )


@pytest.mark.asyncio
async def test_verify_without_otp_code(adapter: FreedomBankOTPAdapter):
    """
        Ошибка валидации, нет otp_code
    """
    with pytest.raises(OTPValidationError, match="otp_code is required"):
        await adapter.verify(
            partner_order_id="BFF000056",
            otp_code="",
        )


@pytest.mark.asyncio
async def test_verify_wrong_combinations_in_client_side(adapter: FreedomBankOTPAdapter):
    """
        Клиент вернул ошибку NOT_FOUND в теле ответа, обрабатываем ее
    """
    with pytest.raises(OTPBadRequestError, match="wrong combinations of phone_number and request_id in client side"):
        await adapter.verify(
            partner_order_id="BFF000056",
            otp_code="1111",
        )

@pytest.mark.asyncio
async def test_verify_wrong_otp_during_verification_client_side(adapter: FreedomBankOTPAdapter):
    """
        Клиент вернул ошибку FAILURE в теле ответа, обрабатываем ее
    """
    with pytest.raises(OTPWrongOTPCode, match="wrong OTP, error OTP code verification in client side"):
        await adapter.verify(
            partner_order_id="BFF000056",
            otp_code="3333",
        )
