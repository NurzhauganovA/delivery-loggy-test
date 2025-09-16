from unittest.mock import AsyncMock, patch

import pytest
from httpx import Response, Request

from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
@patch(
    'api.clients.pos_terminal.client.POSTerminalClient.registrate_pos_terminal',
    new=AsyncMock(
        return_value=Response(
            status_code=200,
            request=Request("POST", "http://example.com/test"),
            json={
                "id": "3bd7f704-3f78-11f0-8fd1-fa6a92be66cf",
                "definitionId": "OverdraftTMSProcess",
                "businessKey": "OVERDRAFT-TMS25-02263",
                "caseInstanceId": None,
                "taskId": None,
                "tenantId": None,
                "ended": False,
                "suspended": False,
                "inventory_number": "123456789",
                "sum": 10000.1
            }
        )
    )
)
@pytest.mark.asyncio
async def test_transition_pos_terminal_registration(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    """
        Проверяем переход на статус pos_terminal_registration
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    # Получаем продукт у заявки и видим что у терминала нет модели и серийного номера
    response = await client.get(
        url='/v1/order/1/product/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    attributes = response.json().get('attributes')
    assert attributes.get('model') is None
    assert attributes.get('serial_number') is None

    # Регистрируем терминал, передвигая его на статус pos_terminal_registration
    response = await client.put(
        url='/v2/order/1/status',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            'payload': {
                'model': 'PAX',
                'serial_number': '999111888222777',
            }
        },
        params={
            'status_id': '36',
        }
    )
    assert response.status_code == 200

    # Получаем продукт у заявки и видим что у терминала появились модель и серийный номер
    response = await client.get(
        url='/v1/order/1/product/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    attributes = response.json().get('attributes')
    assert attributes.get('model') == 'PAX'
    assert attributes.get('serial_number') == '999111888222777'
    assert attributes.get('business_key') == 'OVERDRAFT-TMS25-02263'


@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
@patch(
    'api.clients.pos_terminal.client.POSTerminalClient.registrate_pos_terminal',
    new=AsyncMock(
        return_value=Response(
            status_code=200,
            request=Request("POST", "http://example.com/test"),
            json={
                "id": "3bd7f704-3f78-11f0-8fd1-fa6a92be66cf",
                "definitionId": "OverdraftTMSProcess",
                "businessKey": "OVERDRAFT-TMS25-02263",
                "caseInstanceId": None,
                "taskId": None,
                "tenantId": None,
                "ended": False,
                "suspended": False,
            }
        )
    )
)
@pytest.mark.asyncio
async def test_empty_body(
        client,
        credentials,
        profile_data,
        get_access_token_v1,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    """
        Проверяем переход на статус pos_terminal_registration
    """
    await run_pre_start_sql_script(pre_start_sql_script)

    access_token = await get_access_token_v1(client, credentials, profile_data)

    # Получаем продукт у заявки и видим что у терминала нет модели и серийного номера
    response = await client.get(
        url='/v1/order/1/product/1',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 200
    attributes = response.json().get('attributes')
    assert attributes.get('model') is None
    assert attributes.get('serial_number') is None

    # Регистрируем терминал, передвигая его на статус pos_terminal_registration
    response = await client.put(
        url='/v2/order/1/status',
        headers={'Authorization': 'Bearer ' + access_token},
        params={
            'status_id': '36',
        }
    )
    assert response.status_code == 400
    assert response.json() == {'detail': 'data is required', 'status': 'bad_request', 'status_code': 400}
