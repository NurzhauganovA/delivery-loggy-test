from tortoise.models import Model
from tortoise import fields

from api import models
from api.models.fields import ImageField


# TODO LG-252: Переименовать в OrderComment или внизу заменить на CommentImage
class Comment(Model):
    id = fields.IntField(pk=True)
    order: fields.ForeignKeyRelation['models.Order'] = fields.ForeignKeyField(
        model_name='versions.Order',
        related_name='comments',
        on_delete=fields.CASCADE,
    )
    user: fields.ForeignKeyRelation['models.User'] = fields.ForeignKeyField(
        model_name='versions.User',
        related_name='comments',
        on_delete=fields.SET_NULL,
        null=True,
    )
    # в случае пользователь будет удален, на основе полей ниже можем отобразить автора комментария.
    user_name = fields.CharField(max_length=255)
    user_role: fields.ReverseRelation['models.Group'] = fields.ForeignKeyField(
        model_name='versions.Group',
        related_name='comments',
        on_delete=fields.RESTRICT,
        to_field='slug',
    )

    text = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    # type hints
    order_id: int
    user_id: int | None
    user_role_id: int

    class Meta:
        table = 'order_comment'


class CommentImage(Model):
    id = fields.IntField(pk=True)
    comment: fields.ForeignKeyRelation[Comment] = fields.ForeignKeyField(
        'versions.Comment',
        related_name='images',
        on_delete=fields.CASCADE,
    )
    image = ImageField(upload_to='comments')

    # type hints
    comment_id: int

    class Meta:
        table = 'order_comment_image'
