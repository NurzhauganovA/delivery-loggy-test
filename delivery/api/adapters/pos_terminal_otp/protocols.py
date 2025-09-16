from typing import Protocol

from httpx import HTTPStatusError, Response


class PosTerminalOTPClientProtocol(Protocol):
    """Интерфейс клиента для работы с внешним сервисом ОТП"""
    async def send(
        self,
        business_key: str,
        phone_number: str,
    ) -> Response | HTTPStatusError:
        ...

    async def verify(
        self,
        business_key: str,
        phone_number: str,
        otp_code: str,
        courier_full_name: str,
    ) -> Response | HTTPStatusError:
        ...
