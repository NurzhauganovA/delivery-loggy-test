from typing import List

from .. import exceptions
from .. import models
from .. import schemas


async def category_get_list(partner_id: int) -> List[schemas.CategoryGet]:
    return await models.category_get_list(partner_id)


async def category_get(category_id: int, **kwargs) -> schemas.CategoryGet:
    return await models.category_get(category_id=category_id, **kwargs)


async def category_create(
    category: schemas.CategoryCreate,
    **kwargs,
) -> schemas.CategoryGet:
    return await models.category_create(category, **kwargs)


async def category_update(
    category_id: int,
    update: schemas.CategoryUpdate,
) -> schemas.CategoryGet:
    return await models.category_update(category_id, update)


async def category_delete(category_id: int) -> None:
    return await models.category_delete(category_id)


async def category_delete_bulk(
    category_ids: schemas.CategoryIds,
) -> None:
    return await models.category_delete_bulk(category_ids)
