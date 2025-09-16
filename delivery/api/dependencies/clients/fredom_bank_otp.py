from api.clients.freedom_bank_otp import FreedomBankOTPClient
from api.conf import conf

__freedom_bank_otp_client: FreedomBankOTPClient | None = None

async def get_freedom_bank_otp_client() -> FreedomBankOTPClient:
    global __freedom_bank_otp_client
    if __freedom_bank_otp_client is None:
        __freedom_bank_otp_client = FreedomBankOTPClient(
            base_url=conf.freedom_bank_otp.base_url,
            username=conf.freedom_bank_otp.username,
            password=conf.freedom_bank_otp.password,
        )

    return __freedom_bank_otp_client


async def aclose_freedom_bank_otp_client() -> None:
    if __freedom_bank_otp_client is not None:
        await __freedom_bank_otp_client.aclose()
