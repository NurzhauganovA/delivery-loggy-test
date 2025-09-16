from typing import Protocol

from httpx import Response, HTTPStatusError


class FreedomBankOTPProtocol(Protocol):
    """Интерфейс клиента для работы с внешним сервисом ОТП"""
    async def send(self, request_id: str) -> Response | HTTPStatusError:
        ...

    async def verify(self, request_id: str, otp_code: str) -> Response | HTTPStatusError:
        ...
