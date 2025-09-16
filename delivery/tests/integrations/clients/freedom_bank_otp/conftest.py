import pytest_asyncio

from api.clients.freedom_bank_otp import FreedomBankOTPClient


@pytest_asyncio.fixture(scope="session")
async def client():
    client = FreedomBankOTPClient(
        base_url="https://dev-2-all-proxy-in-one.trafficwave.kz/bank/loggy/delivery/otp",
        username="loggy",
        password="tNvpwH4HH8GGjPFYtjcEwR==",
    )

    yield client

    await client.aclose()
