from unittest.mock import patch, AsyncMock

import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def get_access_token_v1():

    @patch('api.services.sms.otp.OTP.check_otp', new=AsyncMock(return_value=None))
    async def wrapper(client: AsyncClient, credentials: dict[str, str], profile_data: dict[str, str]) -> str:
        profile_type = profile_data['profile_type']
        profile_id = profile_data['profile_id']
        response = await client.post(
            f'/v1/token?profile_type={profile_type}&profile_id={profile_id}',
            data=credentials,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            }
        )
        data = response.json()
        return data['access_token']

    return wrapper
