from httpx import (
    Response,
    AsyncClient,
    HTTPStatusError,
)

from api.utils.logging import log_client_request


class PosTerminalOTPClient:
    def __init__(self, base_url: str, auth_header: str):
        headers = {
            'Authorization': auth_header,
        }
        self.__client = AsyncClient(
            timeout=15.0,
            base_url=base_url,
            headers=headers,
        )

    async def aclose(self):
        await self.__client.aclose()

    @log_client_request(
        client_name="pos_terminal",
        method_name="send"
    )
    async def send(self, business_key: str, phone_number: str) -> Response | HTTPStatusError:
        params = {
            'phoneNumber': phone_number,
        }

        response = await self.__client.post(
            url=f'/tms/send-otp/{business_key}',
            params=params
        )

        return response

    @log_client_request(
        client_name="pos_terminal",
        method_name="verify"
    )
    async def verify(
        self,
        business_key: str,
        phone_number: str,
        otp_code: str,
        courier_full_name: str,
    ) -> Response | HTTPStatusError:
        params = {
            'phoneNumber': phone_number,
            'otpCode': otp_code,
            'managerFio': courier_full_name,
        }

        response = await self.__client.post(
            url=f'/tms/user-task/complete/{business_key}',
            params=params,
        )

        return response
