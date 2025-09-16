from typing import BinaryIO

from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q

from api import schemas, models


async def attach_image_to_comment(
    order_id: int,
    order_filters: list[Q],
    comment_id: int,
    current_user: schemas.UserCurrent,
    image: BinaryIO,
) -> int:
    try:
        await models.Order.get(*order_filters, id=order_id)
    except DoesNotExist:
        raise DoesNotExist('Order does not exist')

    try:
        comment_obj = await models.Comment.get(user_id=current_user.id, order_id=order_id, id=comment_id)
    except DoesNotExist:
        raise DoesNotExist('Comment does not exist')

    comment = await models.CommentImage.create(
        comment=comment_obj,
        image=image,
    )

    return comment.id
