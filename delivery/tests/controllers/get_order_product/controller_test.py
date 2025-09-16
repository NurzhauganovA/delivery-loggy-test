import pytest

from api.controllers.get_order_product import get_order_product, OrderProductNotFoundError
from tests.fixtures.database import db, run_pre_start_sql_script


@pytest.mark.asyncio
async def test_get_order_product(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 1
    product_id = 1

    product = await get_order_product(
        order_id=order_id,
        product_id=product_id,
        default_filter_args=[],
    )

    assert product.id == product_id
    assert product.order_id == order_id
    assert product.type == 'card'
    assert product.attributes == {'pan': '5269********3427'}


@pytest.mark.asyncio
async def test_get_order_product_wrong_order_id(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 2
    product_id = 1

    with pytest.raises(OrderProductNotFoundError, match='product not found'):
         await get_order_product(
            order_id=order_id,
            product_id=product_id,
            default_filter_args=[],
        )


@pytest.mark.asyncio
async def test_get_order_product_wrong_product_id(
        db,
        pre_start_sql_script,
        run_pre_start_sql_script,
):
    await run_pre_start_sql_script(pre_start_sql_script)

    order_id = 1
    product_id = 2

    with pytest.raises(OrderProductNotFoundError, match='product not found'):
         await get_order_product(
            order_id=order_id,
            product_id=product_id,
            default_filter_args=[],
        )
