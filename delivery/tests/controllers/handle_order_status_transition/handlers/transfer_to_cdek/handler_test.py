import pytest

from unittest.mock import patch

from api import models
from tests.fixtures.database import(
    db,
    run_pre_start_sql_script,
)

from tests.utils.json_fixture import get_case_json

from api.controllers.handle_order_status_transition.handlers.transfer_to_cdek.exceptions import(
    CDEKValidationError,
)


@pytest.mark.asyncio
async def test_transfer_to_sdek_handler_valid(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        valid,
        handler,
        expected,
):

    await run_pre_start_sql_script(pre_start_sql_script)
    order_id = valid.pop('order_id')

    status = await models.Status.get(slug='transfer_to_cdek')
    order = await models.Order.get(id=order_id)

    await handler.handle(
        order_obj=order,
        status=status,
        data=valid,
    )
    order = await models.Order.get(id=order_id)
    assert order.track_number is not expected['track_number']
    assert order.delivery_status == expected['delivery_status']


@pytest.mark.asyncio
async def test_transfer_to_sdek_handler_invalid_data(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        invalid,
        handler,
):

    await run_pre_start_sql_script(pre_start_sql_script)
    order_id = invalid.pop('order_id')

    status = await models.Status.get(slug='transfer_to_cdek')
    order = await models.Order.get(id=order_id)

    with pytest.raises(CDEKValidationError) as excinfo:
        await handler.handle(
            order_obj=order,
            status=status,
            data=invalid,
        )
    assert 'invalid body for CDEK order' in str(excinfo.value)
