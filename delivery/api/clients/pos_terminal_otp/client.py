from httpx import Response, AsyncClient, HTTPStatusError, RequestError

from api.logging_module import logger


class PosTerminalOTPClient:
    def __init__(self, base_url: str, auth_header: str):
        headers = {
            'Authorization': auth_header,
        }
        self.__client = AsyncClient(
            base_url=base_url,
            headers=headers,
        )

    async def aclose(self):
        await self.__client.aclose()

    async def send(self, business_key: str, phone_number: str) -> Response | HTTPStatusError:
        params = {
            'phoneNumber': phone_number,
        }

        try:
            response = await self.__client.post(
                url=f'/tms/send-otp/{business_key}',
                params=params
            )
        except RequestError as e:
            logger.error(e)
            raise e

        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            logger.bind(
                status_code=response.status_code,
                method="POST",
                url=str(response.url),
                params=params,
                response=response.text,
            ).error(e)
            raise e

        return response

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

        try:
            response = await self.__client.post(
                url=f'/tms/user-task/complete/{business_key}',
                params=params,
            )
        except RequestError as e:
            logger.error(e)
            raise e

        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            logger.bind(
                status_code=response.status_code,
                method="POST",
                url=str(response.url),
                params=params,
                response=response.text,
            ).error(e)
            raise e

        return response
