from httpx import HTTPStatusError

from api.controllers.handle_order_status_transition.handlers.send_otp.protocols import FreedomBankSendOTPProtocol
from api.controllers.handle_order_status_transition.handlers.verify_otp.protocols import FreedomBankVerifyOTPProtocol
from .exceptions import (
    OTPValidationError,
    OTPBadRequestError,
    OTPWrongOTPCode,
)
from .protocols import FreedomBankOTPProtocol


class FreedomBankOTPAdapter(
    FreedomBankSendOTPProtocol,
    FreedomBankVerifyOTPProtocol,
):
    def __init__(self, client: FreedomBankOTPProtocol):
        self.__client = client

    async def send(self, partner_order_id: str) -> None:
        if not partner_order_id:
            raise OTPValidationError("partner_order_id is required")

        await self.__send(
            partner_order_id=partner_order_id,
        )

    async def verify(self, partner_order_id: str, otp_code: str) -> None:
        if not partner_order_id:
            raise OTPValidationError("partner_order_id is required")

        if not otp_code:
            raise OTPValidationError("otp_code is required")

        await self.__verify(
            partner_order_id=partner_order_id,
            otp_code=otp_code,
        )

    async def __send(self, partner_order_id: str) -> None:
        try:
            await self.__client.send(
                request_id=partner_order_id,
            )
        except HTTPStatusError as e:
            raise OTPBadRequestError("can not send otp, bad request") from e

    async def __verify(self, partner_order_id: str, otp_code: str) -> None:
        try:
            response = await self.__client.verify(
                request_id=partner_order_id,
                otp_code=otp_code,
            )
        except HTTPStatusError as e:
            raise OTPBadRequestError("can not verify otp, bad request") from e

        if response.json().get("payload") == "NOT_FOUND":
            raise OTPBadRequestError("wrong combinations of phone_number and request_id in client side")

        if response.json().get("payload") == "FAILURE":
            raise OTPWrongOTPCode("wrong OTP, error OTP code verification in client side")
