import pytest

from api.adapters.pos_terminal_otp import (
    PosTerminalOTPAdapter,
    OTPValidationError,
    OTPBadRequestError,
    OTPInvalidOTPCode,
)


@pytest.mark.asyncio
async def test_send(adapter: PosTerminalOTPAdapter) -> None:
    """
        Ошибки быть не должно, send вернет None
    """
    await adapter.send(
        business_key='OVERDRAFT-00000000',
        phone_number='+77000000000',
    )


@pytest.mark.asyncio
async def test_send_and_verify(adapter: PosTerminalOTPAdapter) -> None:
    """
        Ошибки быть не должно
    """
    await adapter.send(
        business_key='OVERDRAFT-00000000',
        phone_number='+77000000000',
    )

    await adapter.verify(
        business_key='OVERDRAFT-00000000',
        phone_number='+77000000000',
        otp_code='1234',
        courier_full_name='<NAME>',
    )


@pytest.mark.asyncio
async def test_verify_without_send(adapter: PosTerminalOTPAdapter):
    """
        Ошибка получения request_id из хранилища, возвращаем ошибку адаптера
    """
    with pytest.raises(OTPBadRequestError, match='invalid phone_number in client side'):
        await adapter.verify(
            business_key='OVERDRAFT-00000000',
            phone_number='+77000000000',
            otp_code='4444',
            courier_full_name='<NAME>',
        )


@pytest.mark.asyncio
async def test_send_bad_request(adapter: PosTerminalOTPAdapter):
    """
        Ошибка HTTP с кодом 500, возвращаем ошибку адаптера
    """
    with pytest.raises(OTPBadRequestError, match='can not send otp, bad request'):
        await adapter.send(
            business_key='OVERDRAFT-00000000',
            phone_number='+77000000002',
        )


@pytest.mark.asyncio
async def test_send_without_business_key(adapter: PosTerminalOTPAdapter):
    """
        Ошибка валидации, нет business_key
    """
    with pytest.raises(OTPValidationError, match='business_key is required'):
        await adapter.send(
            business_key='',
            phone_number='+77000000002',
        )


@pytest.mark.asyncio
async def test_send_without_phone_number(adapter: PosTerminalOTPAdapter):
    """
        Ошибка валидации, нет phone_number
    """
    with pytest.raises(OTPValidationError, match='phone_number is required'):
        await adapter.send(
            business_key='OVERDRAFT-00000000',
            phone_number='',
        )


@pytest.mark.asyncio
async def test_verify_bad_request(adapter: PosTerminalOTPAdapter):
    """
        Ошибка HTTP с кодом 500, возвращаем ошибку адаптера
    """
    await adapter.send(
        business_key='OVERDRAFT-00000000',
        phone_number='+77000000000',
    )

    with pytest.raises(OTPBadRequestError, match='can not verify otp, bad request'):
        await adapter.verify(
            business_key='OVERDRAFT-00000000',
            phone_number='+77000000000',
            otp_code='2222',
            courier_full_name='<NAME>',
        )


@pytest.mark.asyncio
async def test_verify_without_business_key(adapter: PosTerminalOTPAdapter):
    """
        Ошибка валидации, нет business_key
    """
    await adapter.send(
        business_key='OVERDRAFT-00000000',
        phone_number='+77000000000',
    )

    with pytest.raises(OTPValidationError, match='business_key is required'):
        await adapter.verify(
            business_key='',
            phone_number='+77000000000',
            otp_code='1234',
            courier_full_name='<NAME>',
        )


@pytest.mark.asyncio
async def test_verify_without_phone_number(adapter: PosTerminalOTPAdapter):
    """
        Ошибка валидации, нет phone_number
    """
    await adapter.send(
        business_key='OVERDRAFT-00000000',
        phone_number='+77000000000',
    )

    with pytest.raises(OTPValidationError, match='phone_number is required'):
        await adapter.verify(
            business_key='OVERDRAFT-00000000',
            phone_number='',
            otp_code='1234',
            courier_full_name='<NAME>',
        )


@pytest.mark.asyncio
async def test_verify_without_otp_code(adapter: PosTerminalOTPAdapter):
    """
        Ошибка валидации, нет otp_code
    """
    await adapter.send(
        business_key='OVERDRAFT-00000000',
        phone_number='+77000000000',
    )

    with pytest.raises(OTPValidationError, match='otp_code is required'):
        await adapter.verify(
            business_key='OVERDRAFT-00000000',
            phone_number='+77000000000',
            otp_code='',
            courier_full_name='<NAME>',
        )


@pytest.mark.asyncio
async def test_verify_without_courier_full_name(adapter: PosTerminalOTPAdapter):
    """
        Ошибка валидации, нет courier_full_name
    """
    await adapter.send(
        business_key='OVERDRAFT-00000000',
        phone_number='+77000000000',
    )

    with pytest.raises(OTPValidationError, match='courier_full_name is required'):
        await adapter.verify(
            business_key='OVERDRAFT-00000000',
            phone_number='+77000000000',
            otp_code='1234',
            courier_full_name='',
        )


@pytest.mark.asyncio
async def test_verify_invalid_otp_during_verification_client_side(adapter: PosTerminalOTPAdapter):
    """
        Клиент вернул ошибку FAILURE в теле ответа, обрабатываем ее
    """
    await adapter.send(
        business_key='OVERDRAFT-00000000',
        phone_number='+77000000000',
    )

    with pytest.raises(OTPInvalidOTPCode, match='invalid OTP, error OTP code verification in client side'):
        await adapter.verify(
            business_key='OVERDRAFT-00000000',
            phone_number='+77000000000',
            otp_code='3333',
            courier_full_name='<NAME>',
        )
