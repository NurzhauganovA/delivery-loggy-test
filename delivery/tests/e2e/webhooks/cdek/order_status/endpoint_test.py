import pytest

from tests.fixtures.client import client
from tests.fixtures.database import (
    db,
    run_pre_start_sql_script,
)


@pytest.mark.asyncio
async def test_webhook_success(
        client,
        body,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key
):
    await run_pre_start_sql_script(pre_start_sql_script)

    response = await client.post(
        url='/v2/webhooks/cdek/order-status',
        data=body,
        params={
            'api_key': api_key,
        }
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_wrong_api_key(
        client,
        body,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    response = await client.post(
        url='/v2/webhooks/cdek/order-status',
        data=body,
        params={
            'api_key': "1111",
        }
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_not_found_order_by_uuid(
        client,
        body_with_wrong_uuid,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        api_key
):
    await run_pre_start_sql_script(pre_start_sql_script)

    response = await client.post(
        url='/v2/webhooks/cdek/order-status',
        data=body_with_wrong_uuid,
        params={
            'api_key': api_key,
        }
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Object does not exist', 'status': 'not-found', 'status_code': 404}
