from tortoise import Model
from tortoise import fields

from .order import Order


class Product(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    order: fields.OneToOneRelation['Order'] = fields.OneToOneField(
        model_name='versions.Order',
        related_name='product',
    )
    type = fields.CharField(max_length=20)
    name = fields.CharField(max_length=100, null=True)
    attributes = fields.JSONField(null=False)

    # Временное поле индекс для поиска и фильтрации, потом переделаем все через поле attributes
    pan_suffix = fields.CharField(max_length=4, null=True)

    # type hints
    order_id: int

    class Meta:
        table = 'product'
        indexes = [('pan_suffix',)]
