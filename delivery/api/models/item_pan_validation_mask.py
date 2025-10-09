import tortoise.transactions

from tortoise import fields


class ItemPanValidationMask(tortoise.models.Model):
    item = fields.ForeignKeyField(
        model_name='versions.Item',
        on_delete=fields.CASCADE,
        null=False,
    )
    mask = fields.CharField(max_length=16, null=False)

    class Meta:
        table = 'item_pan_validation_mask'
        unique_together = (('item', 'mask'),)
