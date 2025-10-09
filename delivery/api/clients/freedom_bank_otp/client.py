from httpx import (
    Response,
    AsyncClient,
    BasicAuth,
    HTTPStatusError,
)

from api.utils.logging import log_client_request


class FreedomBankOTPClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.__client = AsyncClient(
            timeout=15.0,
            auth=BasicAuth(username, password),
            base_url=base_url,
        )

    async def aclose(self):
        await self.__client.aclose()

    @log_client_request(
        client_name="freedom_bank_otp",
        method_name="send"
    )
    async def send(self, request_id: str) -> Response | HTTPStatusError:
        params = {
            "requestId": request_id,
        }

        response = await self.__client.post(
            url="/send",
            params=params,
        )

        # Проверим ошибки при HTTP статусе 200
        data = response.json()

        if data.get("errorCode") == "ERROR":
            raise HTTPStatusError(
                message="bad response, errorCode: ERROR",
                request=response.request,
                response=response,
            )

        return response

    @log_client_request(
        client_name="freedom_bank_otp",
        method_name="verify"
    )
    async def verify(self, request_id: str, otp_code: str) -> Response | HTTPStatusError:
        params = {
            "requestId": request_id,
            "otp": otp_code,
        }

        response = await self.__client.post(
            url="/verify",
            params=params,
        )

        # Проверим ошибки при HTTP статусе 200
        data = response.json()

        if data.get("payload") == "NOT_FOUND":
            raise HTTPStatusError(
                message="bad response, payload: NOT_FOUND",
                request=response.request,
                response=response,
            )

        elif data.get("payload") == "FAILURE":
            raise HTTPStatusError(
                message="bad response, payload: FAILURE",
                request=response.request,
                response=response,
            )

        return response
