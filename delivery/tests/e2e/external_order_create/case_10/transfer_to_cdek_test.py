import pytest
from unittest.mock import patch

from tests.fixtures.client import client
from tests.fixtures.database import(
    db,
    run_pre_start_sql_script,
)

from api.models import Order
from api.controllers.external_order_create import external_order_create
from api.dependencies.adapters.cdek import get_cdek_adapter


@pytest.mark.asyncio
async def test_transfer_to_cdek(
        client,
        api_key,
        body,
        expected,
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        mock_value,
):
    """
        Создание заявки для передачи в CDEK
    """

    cdek_adapter = await get_cdek_adapter()
    cdek_adapter.order_create = mock_value
    await run_pre_start_sql_script(pre_start_sql_script)
    response = await client.post(
        url='/v1/external/order/create',
        data=body,
        params={
            'api_key': api_key,
        },
    )
    assert response.status_code == 200, response.content
    order = await Order.get(id=1)
    current_status = await order.current_status.first()
    assert current_status.slug == expected['current_status'], current_status.slug
    assert order.courier_service == expected['courier_service'], order.courier_service
    assert order.delivery_status == expected['delivery_status'], order.delivery_status
