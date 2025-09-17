from unittest.mock import patch, AsyncMock

import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@patch(
    target='api.adapters.freedom_bank_otp.adapter.FreedomBankOTPAdapter.send',
    new_callable=AsyncMock,
)
@patch(
    target='api.models.order_sms_postcontrol',
    new_callable=AsyncMock,
)
async def test_use_our_otp_service(
        mock_our_otp_send,
        mock_partner_otp_send,
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    response = await client.post(
        url='/v1/order/1/sms-postcontrol',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'latitude': 11.11,
            'longitude': 22.22,
        }
    )
    assert response.status_code == 200

    assert not mock_partner_otp_send.called

    assert mock_our_otp_send.called
