from api.clients.pos_terminal_otp import PosTerminalOTPClient
from api.conf import conf

__pos_terminal_otp_client: PosTerminalOTPClient | None = None

async def get_pos_terminal_otp_client() -> PosTerminalOTPClient:
    global __pos_terminal_otp_client
    if __pos_terminal_otp_client is None:
        __pos_terminal_otp_client = PosTerminalOTPClient(
            base_url=conf.pos_terminal_otp.base_url,
            auth_header=conf.pos_terminal_otp.auth_header,
        )

    return __pos_terminal_otp_client


async def aclose() -> None:
    if __pos_terminal_otp_client is not None:
        await __pos_terminal_otp_client.aclose()
