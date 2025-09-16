import json
from unittest.mock import patch, AsyncMock

import pytest

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@patch('api.services.sms.notification.send_message_to_notification_service', new=AsyncMock(return_value=None))
async def test_create_general_call_center_manager_with_new_user(
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

    data = {
        'user': {
            'phone_number': '+77777777773',
        },
        'profile_type': 'general_call_center_manager',
        'profile_content': {
            'partner_id': 1,
        }
    }

    response = await client.post(
        url='/v1/profile',
        headers={'Authorization': 'Bearer ' + access_token},
        data=json.dumps(data),
    )

    assert response.status_code == 201
    assert response.json() == {
        'id': 1,
        'profile_content': {
            'partner_id': 1,
            'user_id': 4,
        },
        'profile_type': 'general_call_center_manager',
        'user_id': 4,
    }


@pytest.mark.asyncio
@patch('api.services.sms.notification.send_message_to_notification_service', new=AsyncMock(return_value=None))
async def test_create_general_call_center_manager_with_existing_user(
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

    data = {
        'user': {
            'phone_number': '+77777777777',
        },
        'profile_type': 'general_call_center_manager',
        'profile_content': {
            'partner_id': 1,
            'country_id': 1,
        }
    }

    response = await client.post(
        url='/v1/profile',
        headers={'Authorization': 'Bearer ' + access_token},
        data=json.dumps(data),
    )

    assert response.status_code == 201
    assert response.json() == {
        'id': 1,
        'profile_content': {
            'partner_id': 1,
            'user_id': 1
        },
        'profile_type': 'general_call_center_manager',
        'user_id': 1
    }


@pytest.mark.asyncio
@patch('api.services.sms.notification.send_message_to_notification_service', new=AsyncMock(return_value=None))
async def test_create_general_call_center_manager_with_invalid_partner_id(
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

    data = {
        'user': {
            'phone_number': '+77777777775',
        },
        'profile_type': 'general_call_center_manager',
        'profile_content': {
            'partner_id': 0,
        }
    }

    response = await client.post(
        url='/v1/profile',
        headers={'Authorization': 'Bearer ' + access_token},
        data=json.dumps(data),
    )

    assert response.status_code == 400
    response_data = response.json()
    assert 'detail' in response_data
    assert response_data['detail'] == 'Partner with given ID: 0 was not found'
