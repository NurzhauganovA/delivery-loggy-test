from tortoise import Model
from tortoise import fields
from tortoise.exceptions import DoesNotExist

from .. import enums
from .. import schemas


class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    item_type = fields.CharEnumField(**enums.ItemType.to_kwargs())
    value = fields.IntField()
    partner = fields.ForeignKeyField(
        'versions.Partner',
        'categories',
    )

    # type hints
    partner_id: int

    class Config:
        extra = 'forbid'

    class Meta:
        table = 'categories'


async def category_get_list(partner_id: int):
    result = await Category.filter(partner_id=partner_id).values()
    return result


async def category_get(category_id: int, **kwargs):
    try:
        result = await Category.get(id=category_id, **kwargs).values()
    except DoesNotExist:
        raise DoesNotExist(
            f'category with given ID: {category_id} was not found',
        )
    return result


async def category_create(
    category: schemas.CategoryCreate,
    **kwargs,
):
    result = await Category.create(**category.dict(), **kwargs)
    return dict(result)


async def category_update(
    category_id: int,
    update: schemas.CategoryUpdate,
):
    category = await Category.get(id=category_id)

    await category.update_from_dict(update.dict()).save()

    return dict(category)


async def category_delete(category_id: int) -> None:
    category = await Category.get(id=category_id)
    await category.delete()


async def category_delete_bulk(
    category_ids: schemas.CategoryIds,
) -> None:
    await Category.filter(id__in=category_ids.items).delete()
