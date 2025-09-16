from httpx import Response, AsyncClient, BasicAuth, HTTPStatusError, RequestError

from api.logging_module import logger


class FreedomBankOTPClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.__client = AsyncClient(
            auth=BasicAuth(username, password),
            base_url=base_url,
        )

    async def aclose(self):
        await self.__client.aclose()

    async def send(self, request_id: str) -> Response | HTTPStatusError:
        params = {
            "requestId": request_id,
        }

        try:
            response = await self.__client.post(
                url="/send",
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

    async def verify(self, request_id: str, otp_code: str) -> Response | HTTPStatusError:
        params = {
            "requestId": request_id,
            "otp": otp_code,
        }

        try:
            response = await self.__client.post(
                url="/verify",
                params=params,
            )
            logger.bind(
                status_code=response.status_code,
                method="POST",
                url=str(response.url),
                params=params,
                response=response.text,
            ).debug(response.request)
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

        # Проверим ошибки при HTTP статусе 200
        data = response.json()

        if data.get("payload") == "NOT_FOUND":
            logger.bind(
                status_code=response.status_code,
                method="POST",
                url=str(response.url),
                params=params,
                response=response.text,
            ).error("verify error: NOT_FOUND")

        if data.get("payload") == "FAILURE":
            logger.bind(
                status_code=response.status_code,
                method="POST",
                url=str(response.url),
                params=params,
                response=response.text,
            ).error("verify error: FAILURE")

        return response
