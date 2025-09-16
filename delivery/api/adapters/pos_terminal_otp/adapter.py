from httpx import HTTPStatusError

from api.controllers.handle_order_status_transition.handlers.send_otp.protocols import PosTerminalSendOTPProtocol
from api.controllers.handle_order_status_transition.handlers.verify_otp.protocols import PosTerminalVerifyOTPProtocol
from .exceptions import (
    OTPValidationError,
    OTPBadRequestError,
    OTPInvalidOTPCode,
)
from .protocols import PosTerminalOTPClientProtocol


class PosTerminalOTPAdapter(
    PosTerminalSendOTPProtocol,
    PosTerminalVerifyOTPProtocol,
):
    def __init__(self, client: PosTerminalOTPClientProtocol):
        self.__client = client

    async def send(self, business_key: str, phone_number: str) -> None:
        if not business_key:
            raise OTPValidationError('business_key is required')
        if not phone_number:
            raise OTPValidationError('phone_number is required')

        await self.__send(
            business_key=business_key,
            phone_number=phone_number,
        )

    async def verify(
        self,
        business_key: str,
        phone_number: str,
        otp_code: str,
        courier_full_name: str,
    ) -> None:
        if not business_key:
            raise OTPValidationError('business_key is required')
        if not phone_number:
            raise OTPValidationError('phone_number is required')
        if not courier_full_name:
            raise OTPValidationError('courier_full_name is required')
        if not otp_code:
            raise OTPValidationError('otp_code is required')

        await self.__verify(
            business_key=business_key,
            phone_number=phone_number,
            otp_code=otp_code,
            courier_full_name=courier_full_name,
        )

    async def __send(self, business_key: str, phone_number: str) -> None:
        try:
            await self.__client.send(
                business_key=business_key,
                phone_number=phone_number,
            )
        except HTTPStatusError as e:
            raise OTPBadRequestError('can not send otp, bad request') from e

    async def __verify(
        self,
        business_key: str,
        phone_number: str,
        otp_code: str,
        courier_full_name: str,
    ) -> None:
        try:
            response = await self.__client.verify(
                business_key=business_key,
                phone_number=phone_number,
                otp_code=otp_code,
                courier_full_name=courier_full_name,
            )
        except HTTPStatusError as e:
            raise OTPBadRequestError('can not verify otp, bad request') from e

        if response.json() == 'NOT_FOUND':
            raise OTPBadRequestError('invalid phone_number in client side')

        if response.json() == 'FAILURE':
            raise OTPInvalidOTPCode('invalid OTP, error OTP code verification in client side')
