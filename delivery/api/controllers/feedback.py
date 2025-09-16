from tortoise.exceptions import DoesNotExist

from .. import exceptions
from .. import models
from .. import schemas


async def feedback_get_list(**kwargs) -> dict:
    return await models.feedback_list(**kwargs)


async def feedback_create_by_manager(feedback: schemas.FeedbackCreateManager, **kwargs):
    return await models.feedback_create(feedback, **kwargs)


async def feedback_create_by_receiver(
    feedback: schemas.FeedbackCreateReceiver,
    **kwargs,
):
    try:
        order = await models.Order.all_objects.get(id=feedback.order_id)
    except DoesNotExist:
        raise DoesNotExist(
            f'Order with given ID: {feedback.order_id} not found',
        )
    kwargs['author_full_name'] = order.receiver_name
    kwargs['author_phone'] = order.receiver_phone_number
    try:
        return await models.feedback_create(feedback, **kwargs)
    except models.FeedbackAlreadyExist as e:
        raise exceptions.HTTPBadRequestException(e)


async def feedback_update_status(
    feedback_id: int,
    update: schemas.FeedbackUpdateStatus,
    **kwargs,
) -> dict:
    return await models.feedback_update_status(feedback_id, update=update, **kwargs)


async def feedback_delete(feedback_id: int, **kwargs) -> None:
    await models.feedback_delete(feedback_id, **kwargs)


async def feedback_get(**kwargs) -> dict:
    return await models.feedback_get(**kwargs)


async def feedback_reason_get_list(**kwargs) -> list:
    return await models.feedback_reason_get_list(**kwargs)


async def feedback_reason_create(
    feedback_reason: schemas.FeedbackReasonCreate,
    **kwargs,
):
    return await models.feedback_reason_create(feedback_reason, **kwargs)


async def feedback_reason_update(
    reason_id: int,
    update: schemas.FeedbackReasonUpdate,
    **kwargs,
):
    return await models.feedback_reason_update(
        reason_id=reason_id,
        update=update,
        **kwargs,
    )


async def feedback_reason_delete(feedback_reason_id: int, **kwargs) -> None:
    await models.feedback_reason_delete(feedback_reason_id, **kwargs)
