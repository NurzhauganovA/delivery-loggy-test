from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q

from api import models, schemas
from .exceptions import OrderProductNotFoundError


async def get_order_product(
        order_id: int,
        product_id: int,
        default_filter_args: list[Q],
) -> schemas.Product:
    # Получим заказ с продуктом
    try:
        order = await models.Order.filter(*default_filter_args).get(id=order_id, product__id=product_id).select_related('product')
    except DoesNotExist as e:
        raise OrderProductNotFoundError('product not found') from e

    # Преобразуем продукт
    product = schemas.Product(
        id=product_id,
        order_id=order_id,
        type=order.product.type,
        attributes=order.product.attributes,
    )

    return product





