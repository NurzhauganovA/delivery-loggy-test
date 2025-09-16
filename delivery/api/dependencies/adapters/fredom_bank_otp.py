from fastapi import Depends

from api.adapters.freedom_bank_otp import (
    FreedomBankOTPAdapter,
    FreedomBankOTPProtocol,
)
from api.dependencies.clients import get_freedom_bank_otp_client

__singleton: FreedomBankOTPAdapter | None = None


async def get_freedom_bank_otp_adapter(
        client: FreedomBankOTPProtocol = Depends(get_freedom_bank_otp_client),
) -> FreedomBankOTPAdapter:
    global __singleton
    if __singleton is None:
        __singleton = FreedomBankOTPAdapter(
            client=client,
        )

    return __singleton
