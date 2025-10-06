from __future__ import annotations

import json
from datetime import datetime
from typing import List

from tortoise.expressions import Q

from .order import get_next_status_from_status
from .partner_callbacks import get_headers
from .publisher import publish_callback
from ..conf import conf
from pydantic import parse_obj_as
from tortoise import Model
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.exceptions import IntegrityError
from tortoise.transactions import atomic

from . import fields as custom_fields
from .mixins import DeleteFilesMixin
from .. import redis_module
from .. import enums
from .. import models
from .. import schemas
from .. import services
from ..enums import OrderStatus


class PostControlCanNotDelete(Exception):
    """Raises when it is not possible to delete a post-control document."""


class PostControlIsNotSubjectToDelete(Exception):
    """Raises when attempting to delete already accepted post-control
    document."""


class PostControlIsNotSubjectToChange(Exception):
    """Raises when attempting to change already accepted post-control
    document."""


class CanNotCompleteOrder(Exception):
    """Raises when OTP code not found to send external API"""


class PostControlNotInOnTheWayToCallPoint(Exception):
    """Raises when accept postcontrol on order not in on the way to call point state"""


class PostControlConfig(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    send = fields.BooleanField(default=False)
    document_code = fields.CharField(max_length=255, null=True)
    item: fields.ForeignKeyRelation['models.Item'] = fields.ForeignKeyField(
        'versions.Item',
        'postcontrol_config_set',
    )
    order = fields.SmallIntField(default=1)
    parent_config: fields.ForeignKeyRelation[PostControlConfig] = fields.ForeignKeyField(
        'versions.PostControlConfig',
        'inner_param_set',
        null=True,
    )

    # type hints
    item_id: int
    postcontrol_document_set: fields.ReverseRelation['models.PostControl']

    class Meta:
        table = 'postcontrol_configs'
        unique_together = ('item', 'name')
        ordering = ('order', )


class PostControl(DeleteFilesMixin, Model):
    order: fields.ForeignKeyRelation['models.Order'] = fields.ForeignKeyField(
        'versions.Order',
        'postcontrol_set',
        on_delete=fields.CASCADE,
    )
    image = custom_fields.ImageField(upload_to='postcontrols')
    config: fields.ForeignKeyNullableRelation['models.PostControlConfig'] = fields.ForeignKeyField(
        'versions.PostControlConfig',
        'postcontrol_document_set',
        fields.SET_NULL,
        null=True,
    )
    type = fields.CharEnumField(
        **enums.PostControlType.to_kwargs(default=enums.PostControlType.POST_CONTROL),
    )
    resolution = fields.CharEnumField(
        **enums.PostControlResolution.to_kwargs(default=enums.PostControlResolution.PENDING))
    comment = fields.TextField(null=True)

    # type hints
    order_id: int
    config_id: int | None

    class Meta:
        table = 'order.postcontrols'
        unique_together = ('order', 'config')


class SMSPostControl(Model):
    otp = fields.SmallIntField()
    created_at: datetime | None = fields.DatetimeField(auto_now_add=True)
    order: fields.ForeignKeyRelation['models.Order'] = fields.ForeignKeyField(
        'versions.Order', 'otp_set')
    try_count = fields.SmallIntField(default=0)
    accepted_at: datetime | None = fields.DatetimeField(null=True)

    # type hints
    order_id: int

    class Meta:
        table = 'order_sms_postcontrols'
        ordering = ('-created_at',)


# TODO: Больше не используется, вместо этого используем Product
class PAN(Model):
    pan = fields.CharField(max_length=20)
    input_type = fields.CharEnumField(
        **enums.InputPanType.to_kwargs(null=True)
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    order: fields.ForeignKeyRelation['models.Order'] = fields.ForeignKeyField(
        'versions.Order',
        'pan_set',
    )
    pan_suffix = fields.CharField(max_length=4, null=True)

    # type hints
    order_id: int

    class Meta:
        table = 'order_pan'
        ordering = ('-created_at',)
        indexes = [('pan_suffix',)]


@atomic()
async def postcontrol_create(order_id: int, image, config_id, default_filter_args, current_user):
    order_obj = await models.Order.filter(*default_filter_args).get(id=order_id)
    instance = await PostControl.create(
        order_id=order_obj.id,
        image=image,
        config_id=config_id,
    )
    order_time = await order_obj.localtime
    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=enums.InitiatorType.USER,
            initiator_id=current_user.id,
            model_type=enums.HistoryModelName.ORDER,
            model_id=order_id,
            request_method=enums.RequestMethods.POST,
            initiator_role=current_user.profile['profile_type'],
            action_data={'post-control': 'created'},
            created_at=order_time,
        )
    )
    await models.OrderStatuses.filter(
        order_id=order_id,
        status_id=int(OrderStatus.POST_CONTROL_BANK.value),
    ).delete()
    if order_obj.current_status_id == int(OrderStatus.POST_CONTROL_BANK.value):
        order_obj.current_status_id = int(OrderStatus.POST_CONTROL.value)
        await order_obj.save()
    config_ids = await PostControlConfig.filter(item_id=order_obj.item_id).values_list('id', flat=True)
    postcontrol_documents = await PostControl.filter(order_id=order_id, config_id__in=config_ids)
    if len(config_ids) == len(postcontrol_documents):
        order_obj.delivery_status = {
            'status': enums.OrderDeliveryStatus.TO_CALL_POINT.value,
            'reason': None,
            'datetime': None,
            'comment': None,
        }
        await order_obj.save()
    return schemas.PostControlGet.from_orm(instance)


async def postcontrol_get_list(order_id: int, default_filter_args: list = None):
    if default_filter_args is None:
        default_filter_args = []
    objects = await PostControl.filter(*default_filter_args, order_id=order_id)
    return parse_obj_as(List[schemas.PostControlGet], objects)


async def postcontrol_get(postcontrol_id: int, default_filter_args: list = None):
    if default_filter_args is None:
        default_filter_args = []
    try:
        instance = await PostControl.get(*default_filter_args, id=postcontrol_id)
        return schemas.PostControlGet.from_orm(instance)
    except DoesNotExist:
        raise DoesNotExist(
            f'Post-control document with provided ID: {postcontrol_id} was not found')


@atomic()
async def postcontrol_make_resolution(resolutions, default_filter_args, user: schemas.UserCurrent):
    documents = []

    for resolution in resolutions:
        postcontrol_id = resolution.id
        try:
            instance = await PostControl.filter(
                *default_filter_args,
            ).distinct().get(id=postcontrol_id)
            instance.resolution = resolution.resolution
            instance.comment = resolution.comment
            await instance.save()
            documents.append(instance)
        except DoesNotExist:
            raise DoesNotExist(
                f'Post-control document with provided '
                f'ID: {postcontrol_id} was not found')

    postcontrols = parse_obj_as(List[schemas.PostControlGet], documents)

    order_obj = await models.Order.select_for_update().get(id=documents[0].order_id)
    if enums.PostControlResolution.DECLINED in (r.resolution for r in resolutions):
        order_obj.delivery_status = {
            'status': enums.OrderDeliveryStatus.BEING_FINALIZED.value,
            'reason': None,
            'datetime': None,
            'comment': None,
        }
        await order_obj.save()
        return postcontrols
    if enums.PostControlResolution.BANK_DECLINED in (r.resolution for r in resolutions):
        order_obj.delivery_status = {
            'status': enums.OrderDeliveryStatus.BEING_FINALIZED_AT_CS.value,
            'reason': None,
            'datetime': None,
            'comment': None,
        }
        await models.OrderStatuses.filter(
            order_id=order_obj.id,
            status_id=int(OrderStatus.POST_CONTROL_BANK.value),
        ).delete()
        prev_status = await models.OrderStatuses.filter(
            order_id=order_obj.id,
        ).order_by('-created_at').first()
        if prev_status:
            order_obj.current_status_id = prev_status.status_id
            await order_obj.save()
        await models.history_create(schemas.HistoryCreate(
            initiator_type=enums.InitiatorType.USER.value,
            initiator_id=user.id,
            request_method=enums.RequestMethods.PUT,
            model_type=enums.HistoryModelName.ORDER,
            model_id=order_obj.id,
            action_data={
                'action': 'post_control_declined_at_bank',
            },
            created_at=await order_obj.localtime,
        ))
        await order_obj.save()
        return postcontrols
    if all((enums.PostControlResolution.ACCEPTED == r.resolution for r in resolutions)):
        config_ids = await PostControlConfig.filter(
            Q(parent_config_id__isnull=True, inner_param_set__isnull=True) | Q(parent_config_id__isnull=False),
            item_id=order_obj.item_id,
        ).values_list('id', flat=True)
        accepted_postcontrols = await PostControl.filter(
            order_id=order_obj.id,
            config_id__in=config_ids,
            resolution=enums.PostControlResolution.ACCEPTED.value,
        ).prefetch_related('config')
        accepted_count = len(accepted_postcontrols)
        if len(config_ids) == accepted_count:

            order_time = await order_obj.localtime
            history_schema = schemas.HistoryCreate(
                initiator_type=enums.InitiatorType.USER.value,
                initiator_id=user.id,
                initiator_role=user.profile['profile_type'],
                request_method=enums.RequestMethods.PUT,
                model_type=enums.HistoryModelName.ORDER,
                model_id=order_obj.id,
                action_data={'post-control': enums.PostControlResolution.ACCEPTED},
                created_at=order_time,
            )
            await models.history_create(history_schema)

            next_status = await get_next_status_from_status(order_obj=order_obj,
                                                            status_slug=enums.StatusSlug.POST_CONTROL)
            if next_status and next_status.id not in (
                int(enums.OrderStatus.DELIVERED.value),
                int(enums.OrderStatus.ISSUED.value),
            ):
                return postcontrols

            order_obj.delivery_status = {
                'status': enums.OrderDeliveryStatus.IS_DELIVERED.value,
                'reason': None,
                'datetime': None,
                'comment': None,
            }
            await order_obj.save()

            if order_obj.type == enums.OrderType.PICKUP:
                final_status = enums.OrderStatus.ISSUED
            else:
                final_status = enums.OrderStatus.DELIVERED
            await models.order_update_status(
                order_obj_or_id=order_obj,
                status_id=final_status,
            )

            await send_photos(accepted_postcontrols, order_obj)
    return postcontrols


@atomic()
async def postcontrol_accept(order_id: int, current_user, default_filter_args: list = None):
    if default_filter_args is None:
        default_filter_args = []
    order_obj = await models.Order.select_for_update().get(*default_filter_args, id=order_id)

    if order_obj.delivery_status.get('status') == enums.OrderDeliveryStatus.CANCELED_AT_CLIENT:
        return

    await PostControl.filter(order_id=order_id).update(
        resolution=enums.PostControlResolution.ACCEPTED.value,
    )

    config_ids = await PostControlConfig.filter(
        Q(parent_config_id__isnull=True, inner_param_set__isnull=True) | Q(parent_config_id__isnull=False),
        item_id=order_obj.item_id,
    ).values_list('id', flat=True)
    config_count = len(config_ids)

    accepted_postcontrols = await PostControl.filter(
        order_id=order_id,
        config_id__in=config_ids,
        resolution=enums.PostControlResolution.ACCEPTED.value,
    ).prefetch_related('config')

    accepted_postcontrol_count = len(accepted_postcontrols)

    #  if postcontrol documents is not empty and all of them are accepted
    if config_count != 0 and config_count == accepted_postcontrol_count:
        #  mark order as delivered
        order_obj.delivery_status = {
            'status': enums.OrderDeliveryStatus.IS_DELIVERED.value,
            'reason': None,
            'datetime': None,
            'comment': None,
        }
        order_time = await order_obj.localtime
        await order_obj.save()

        if order_obj.type == enums.OrderType.PICKUP:
            final_status = enums.OrderStatus.ISSUED
        else:
            final_status = enums.OrderStatus.DELIVERED

        await models.order_update_status(
            order_obj_or_id=order_obj,
            status_id=final_status,
        )

        # send postcontrol documents
        await send_photos(accepted_postcontrols, order_obj)
        history_schema = schemas.HistoryCreate(
            initiator_type=enums.InitiatorType.USER.value,
            initiator_id=current_user.id,
            initiator_role=current_user.profile['profile_type'],
            request_method=enums.RequestMethods.PUT,
            model_type=enums.HistoryModelName.ORDER.value,
            model_id=order_id,
            action_data={'post-control': enums.PostControlResolution.ACCEPTED},
            created_at=order_time,
        )
        await models.history_create(history_schema)


@atomic()
async def postcontrol_decline(order_id: int, default_filter_args: list = None):
    if default_filter_args is None:
        default_filter_args = []
    order = await models.Order.select_for_update().get(*default_filter_args, id=order_id)
    status_map = {
        2: enums.OrderDeliveryStatus.BEING_FINALIZED.value,
        8: enums.OrderDeliveryStatus.VIDEO_PC_BEING_FINALIZED.value,
        9: enums.OrderDeliveryStatus.SMS_PC_BEING_FINALIZED.value,
    }
    delivery_status = enums.OrderDeliveryStatus.BEING_FINALIZED.value
    try:
        delivery_status = status_map[order.deliverygraph_id]
    except KeyError:
        pass
    order.delivery_status = {
        'status': delivery_status,
        'reason': None,
        'datetime': None,
        'comment': None,
    }
    await order.save()
    await PostControl.filter(order_id=order_id).update(resolution=enums.PostControlResolution.DECLINED.value)
    if fcmdevice_ids := await models.FCMDevice.filter(
        user__profile_courier=order.courier_id,
    ).values_list('id', flat=True):
        message = schemas.FirebaseMessage(
            registration_ids=fcmdevice_ids,
            data={
                'title': 'На доработку',
                'description': f'В заявке № {order.id} последконтроль не одобрен. '
                               f'Просьба отработать данную заявку',
                'id': order.id,
                'type': order.type,
                'push_type': enums.PushType.EXC,
                'delivery_status': delivery_status,
            }
        )
        await services.firebase.service.send(message=message)


@atomic()
async def postcontrol_delete(postcontrol_id: int, default_filter_args) -> None:
    try:
        instance = await PostControl.filter(*default_filter_args).distinct().get(id=postcontrol_id)
        if instance.resolution == enums.PostControlResolution.ACCEPTED:
            raise PostControlIsNotSubjectToDelete(
                f'Post-control document with given ID: '
                f'{postcontrol_id} is not subject to delete',
            )
        await instance.delete()
    except DoesNotExist:
        raise DoesNotExist(
            f'Post-control document with given ID: '
            f'{postcontrol_id} was not found',
        )
    except IntegrityError:
        raise PostControlCanNotDelete(
            f'Could not delete post-control object with '
            f'given ID: {postcontrol_id}',
        )


async def send_photos(
    documents: List[PostControl],
    order_obj: models.Order,
):
    send_photo_callback = order_obj.callbacks.get('set_photo', None)
    send_photo_urls_callback = order_obj.callbacks.get('send_photo_urls', None)
    files = []
    for document in documents:
        if not document.config.send:
            continue
        if send_photo_callback:
            files = {'user_photo': document.image}
            conn = redis_module.get_connection()
            await conn.publish(
                channel='send-to-celery',
                message=json.dumps({
                    'task_name': 'send-photo',
                    'kwargs': {'url': send_photo_callback, 'files': files},
                })
            )

        files.append({
            'url': f'https://{conf.api.backend_domain}{document.image}',
            'document_code': document.config.document_code,
        })

    if send_photo_urls_callback:
        # В зависимости от партнера, получаем HTTP заголовки для вызова callback метода
        headers = get_headers(order_obj.partner_id)
        await publish_callback(
            task_name='send-photo-urls',
            url=send_photo_urls_callback,
            data={'files': files},
            headers=headers,
        )
