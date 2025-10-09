import json

import pytest
from tortoise.exceptions import DoesNotExist

from api.views.crm import get_order
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
async def test_get_order(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
        expected,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    result = await get_order(
        order_id=1,
        default_filter_args=[],
    )

    assert json.loads(result.json()) == expected


@pytest.mark.asyncio
async def test_get_order_not_found(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    with pytest.raises(DoesNotExist, match='Object does not exist'):
         await get_order(
            order_id=2,
            default_filter_args=[],
        )
