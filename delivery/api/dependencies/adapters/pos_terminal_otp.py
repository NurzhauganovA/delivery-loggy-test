from fastapi import Depends

from api.adapters.pos_terminal_otp import (
    PosTerminalOTPAdapter,
    PosTerminalOTPClientProtocol,
)
from api.dependencies.clients import get_pos_terminal_otp_client

__pos_terminal_otp_adapter: PosTerminalOTPAdapter | None = None

async def get_pos_terminal_otp_adapter(
        client: PosTerminalOTPClientProtocol = Depends(get_pos_terminal_otp_client),
) -> PosTerminalOTPAdapter:
    global __pos_terminal_otp_adapter
    if __pos_terminal_otp_adapter is None:
        __pos_terminal_otp_adapter = PosTerminalOTPAdapter(
            client=client,
        )

    return __pos_terminal_otp_adapter
