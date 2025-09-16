from typing import Sequence
from typing import Union

from fastapi_pagination.ext.tortoise import paginate
from pydantic import parse_obj_as
from tortoise import Model
from tortoise import fields
from tortoise.query_utils import Prefetch
from tortoise.timezone import now
from tortoise.transactions import atomic

from .. import database
from .. import enums
from .. import models
from .. import schemas


class FeedbackNotFound(Exception):
    """Raises if Feedback with provided ID not found."""


class FeedbackReasonNotFound(Exception):
    """Raises if Feedback reason with provided ID not found."""


class FeedbackAlreadyExist(Exception):
    """Raises if Feedback already has in this order from receiver."""


class FeedbackReason(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=300)
    value = fields.JSONField()
    is_tag = fields.BooleanField()
    partner: fields.ForeignKeyNullableRelation[
        'models.Partner'] = fields.ForeignKeyField(
        'versions.Partner',
        'feedback_reasons',
        null=True,
    )

    # type hints
    partner_id: int

    class Meta:
        table = 'feedback_reason'


class Feedback(Model):
    id = fields.IntField(pk=True)
    reason_set: fields.ManyToManyRelation['FeedbackReason'] = fields.ManyToManyField(
        'versions.FeedbackReason',
        related_name='feedbacks',
    )
    comment = fields.TextField(null=True)
    order: fields.ForeignKeyRelation['models.Order'] = fields.ForeignKeyField(
        'versions.Order',
        'feedback_set',
    )
    rate = fields.SmallIntField()
    final_score = fields.SmallIntField(default=0)
    author_full_name = fields.CharField(max_length=120, null=True)
    author_phone = fields.CharField(max_length=15, null=True)
    author_role = fields.CharEnumField(
        **enums.AuthorsFeedback.to_kwargs(),
        max_length=20,
    )
    status = fields.CharEnumField(
        **enums.FeedbackStatus.to_kwargs(default=enums.FeedbackStatus.NEW),
        max_length=20,
    )
    created_at = fields.DatetimeField(auto_now_add=True, index=True)

    # type hints
    order_id: int

    class Meta:
        table = 'feedback'
        ordering = ('-created_at',)


async def feedback_get(**kwargs):
    feedback = await Feedback.get(**kwargs).prefetch_related(
        Prefetch(
            'reason_set',
            FeedbackReason.all(),
            'reasons',
        )
    ).select_related(
        'order__city',
        'order__item',
        'order__partner',
        'order__courier__user',
        'order__courier__category',
    )

    #  !hardcode
    if courier := feedback.order.courier:
        courier.rate = (await courier.current_rate).value

    return schemas.FeedbackGet.from_orm(feedback)


async def feedback_list(**kwargs):
    params = kwargs.pop('params')
    qs = Feedback.filter(**kwargs).distinct().select_related(
        'order',
        'order__item',
        'order__courier__user',
    )

    return await paginate(qs, params)


@atomic()
async def feedback_create(
    feedback: Union[
        schemas.FeedbackCreateManager,
        schemas.FeedbackCreateReceiver
    ],
    **kwargs,
):
    create_dict = feedback.dict(exclude_unset=True)
    reasons = create_dict.pop('reasons', [])
    if kwargs['author_role'] == enums.AuthorsFeedback.RECEIVER:
        if await Feedback.filter(order_id=feedback.order_id, author_role=enums.AuthorsFeedback.RECEIVER.value).exists():
            raise models.FeedbackAlreadyExist(
                f"Order with provided ID: {feedback.dict().get('order_id')} already has feedback from receiver",
            )
    created = await Feedback.create(
        status=enums.FeedbackStatus.NEW,
        **create_dict,
        **kwargs,
    )
    order_obj = await created.order
    created.created_at = await order_obj.localtime
    if reasons:
        reason_objects = await FeedbackReason.filter(id__in=reasons)
        final_score = 0
        for reason in reason_objects:
            final_score += reason.value.get(str(feedback.rate), 0)
        created.final_score = final_score
        await created.reason_set.add(*reason_objects)
    await created.save()

    await created.fetch_related(
        'order__item',
        'order__partner',
        'order__city',
        'order__courier__user',
        'order__courier__category'
    )
    created.reasons = await created.reason_set

    return schemas.FeedbackGet.from_orm(created)


@atomic()
async def feedback_update_status(
    feedback_id,
    update: schemas.FeedbackUpdateStatus,
    **kwargs,
):
    feedback = await Feedback.get(
        id=feedback_id,
        status=enums.FeedbackStatus.NEW.value,
        **kwargs,
    ).select_related('order')
    await feedback.update_from_dict(update.dict()).save()
    order = await feedback.order
    if feedback.status == enums.FeedbackStatus.APPROVED:
        if order.courier_id:
            created_at = feedback.created_at.replace(
                day=1, hour=0, minute=0,
                second=0, microsecond=0,
            )
            rate = await models.Rate.filter(
                courier_id=order.courier_id,
                created_at=created_at,
            ).first()
            if not rate:
                rate = await models.Rate.create(
                    courier_id=order.courier_id,
                    created_at=created_at,
                )
            rate.value += feedback.final_score
            await rate.save()
    feedback.reasons = await feedback.reason_set
    await feedback.fetch_related(
        'order__item',
        'order__partner',
        'order__city',
        'order__courier__user',
        'order__courier__category'
    )
    return schemas.FeedbackGet.from_orm(feedback)


async def feedback_delete(feedback_id: int, **kwargs):
    feedback = await Feedback.get(id=feedback_id, **kwargs)
    await feedback.delete()


async def feedback_reason_get_list(**kwargs) -> list:
    query = 'SELECT * FROM feedback_reason WHERE partner_id = $1::INT'

    if rate := kwargs.pop('rate', None):
        query += ' AND value ? $2::TEXT'

    async with database.database_connection() as conn:
        stmt = await conn.prepare(query)
        if rate:
            recs = await stmt.fetch(kwargs['partner_id'], str(rate))
        else:
            recs = await stmt.fetch(kwargs['partner_id'])
        result = [dict(row) for row in recs]

    return parse_obj_as(Sequence[schemas.FeedbackReasonGet], result)


async def feedback_reason_create(
    feedback_reason: schemas.FeedbackReasonCreate,
    **kwargs,
):
    reason = await FeedbackReason.create(**feedback_reason.dict(), **kwargs)
    return schemas.FeedbackReasonGet.construct(**dict(reason))


async def feedback_reason_delete(reason_id: int, **kwargs):
    reason = await FeedbackReason.get(id=reason_id, **kwargs)
    await reason.delete()


async def feedback_reason_update(
    reason_id: int,
    update: schemas.FeedbackReasonUpdate,
    **kwargs,
):
    reason = await FeedbackReason.get(id=reason_id, **kwargs)
    await reason.update_from_dict(update.dict(exclude_unset=True)).save()
    return schemas.FeedbackReasonGet.construct(**dict(reason))
