from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.expressions import Q

from api import schemas, models
from api.controllers.comments.create_comment import exceptions
from api.enums import InitiatorType, HistoryModelName, RequestMethods, ActionType


async def create_comment(
    comment_text: str,
    user: schemas.UserCurrent,
    order_id: int,
    order_filters: list[Q],
) -> int:
    try:
        order_obj = await models.Order.get(*order_filters, id=order_id)
    except DoesNotExist:
        raise exceptions.CommentCreateException('Order does not exist')

    order_time = await order_obj.localtime

    try:
        comment = await models.Comment.create(
            text=comment_text,
            order=order_obj,
            user_id=user.id,
            user_name=user.fullname,
            user_role_id=user.profile.get('profile_type'),
            created_at=order_time,
        )
    except IntegrityError as e:
        raise exceptions.CommentCreateException(e)

    await models.history_create(schemas.HistoryCreate(
        initiator_type=InitiatorType.USER,
        initiator_id=user.id,
        initiator_role=user.profile.get('profile_type'),
        request_method=RequestMethods.POST,
        model_type=HistoryModelName.ORDER,
        model_id=order_id,
        action_type=ActionType.CREATE_COMMENT,
        action_data={
            'id': comment.id,
            'text': comment.text,
        },
        created_at=order_time,
    ))

    return comment.id
