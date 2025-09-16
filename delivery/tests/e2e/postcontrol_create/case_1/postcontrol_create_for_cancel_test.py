from unittest.mock import patch, AsyncMock

import pytest

from api.dependencies import get_cancel_image_validator
from api.utils.image.image_validator import ImageValidator
from tests.fixtures.client import client
from tests.fixtures.database import db, run_pre_start_sql_script
from tests.fixtures.token import get_access_token_v1


@pytest.mark.asyncio
@pytest.mark.freeze_uuids
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_postcontrol_create_for_cancel(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    file_57_kb_png,
    file_85_kb_png,
    file_128_kb_png,
    file_151_kb_png,
    expected,
):
    """
    Тестировать создание послед-контроль фотографий для отмены.
    """
    await run_pre_start_sql_script(pre_start_sql_script)
    access_token = await get_access_token_v1(client, credentials, profile_data)

    order_id = 1
    response = await client.post(
        url=f'/v1/post-control/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
        data={
            'config_id': 6,
        },
        files=[file_57_kb_png],
    )
    assert response.status_code == 200
    response = await client.post(
        url=f'/v1/post-control/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
        data={
            'config_id': 7,
        },
        files=[file_85_kb_png],
    )
    assert response.status_code == 200
    response = await client.post(
        url=f'/v1/post-control/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
        data={
            'config_id': 8,
        },
        files=[file_128_kb_png],
    )
    assert response.status_code == 200
    response = await client.post(
        url=f'/v1/post-control/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
        data={
            'config_id': 9,
        },
        files=[file_151_kb_png],
    )
    assert response.status_code == 200

    order_get_response = await client.get(
        url=f'/v1/order/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert order_get_response.status_code == 200
    order_response_data = order_get_response.json()
    item = order_response_data.get('item', dict())
    # Собственно все послед-контроль для отмены должны отображаться в поле postcontrol_cancellation_configs
    assert item.get('postcontrol_cancellation_configs') == expected


@pytest.mark.asyncio
@pytest.mark.freeze_uuids
@patch('api.models.publisher.__publish', new=AsyncMock(return_value=None))
async def test_postcontrol_create_for_cancel_with_too_large_file(
    client,
    credentials,
    profile_data,
    get_access_token_v1,
    db,
    pre_start_sql_script,
    run_pre_start_sql_script,
    file_57_kb_png,
    expected,
):
    app = client._transport.app
    app.dependency_overrides[get_cancel_image_validator] = lambda: ImageValidator(
        max_size=10 * 1024,  # 10 KB
    )
    await run_pre_start_sql_script(pre_start_sql_script)
    access_token = await get_access_token_v1(client, credentials, profile_data)

    order_id = 2
    response = await client.post(
        url=f'/v1/post-control/{order_id}',
        headers={'Authorization': 'Bearer ' + access_token},
        data={'config_id': 6},
        files=[file_57_kb_png],
    )
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Maximum allowed size of the image is 0.01 MB, actual: 0.05 MB',
        'status': 'bad_request',
        'status_code': 400
    }
