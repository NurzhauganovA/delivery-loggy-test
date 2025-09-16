import uuid

from api import exceptions
from api.enums import InitiatorType, HistoryModelName, RequestMethods
from fastapi import UploadFile

from .enums import OrderChainStatus
from .infrastructure.repository import (
    OrderChainStageRepository, OrderChainRepository,
    OrderChainSenderRepository, OrderChainReceiverRepository,
    OrderChainSupportDocumentRepository
)
from tortoise.transactions import atomic
from .schemas.request_schemas import (
    OrderChainCreateModel, OrderChainUpdateModel, OrderChainStageCreateModel, SupportDocumentCreateModel
)
from typing import Union

from .schemas.dto_schemas import OrderChainStageCreateDto, OrderChainGetDto, OrderChainCreateDto, \
    SupportDocumentCreateDto
from ..city.infrastructure.db_table import City
from ... import models, schemas
from ...common.action_base import BaseAction


class OrderChainActions(BaseAction):
    def __init__(self, user=None):
        if user:
            self.user = user
        self.order_chain_repo = OrderChainRepository()
        self.order_chain_sender_repo = OrderChainSenderRepository()
        self.order_chain_receiver_repo = OrderChainReceiverRepository()
        self.order_chain_stage_repo = OrderChainStageRepository()
        self.order_chain_document_repo = OrderChainSupportDocumentRepository()

    async def create_order(
        self,
        order_data: dict,
        partner_id: int,
    ):
        city_name = await City.get(id=order_data['city_id']).values('name')
        return await models.external_order_create(order=schemas.ExternalOrderCreate(
            city=city_name['name'],
            comment=order_data['comment'],
            delivery_datetime=order_data['delivery_datetime'],
            item_id=order_data['item_id'],
            shipment_point_id=order_data.get('shipment_point_id', None),
            receiver_name=order_data['receiver_name'],
            receiver_phone_number=order_data['receiver_phone_number'],
            receiver_iin=order_data.get('receiver_iin', None),
            type=order_data['type'],
            callbacks={},
            address=order_data['address'],
            latitude=order_data['latitude'],
            longitude=order_data['longitude'],
            partner_order_id=order_data['partner_order_id'] if order_data.get(
                'partner_order_id', None
            ) else str(uuid.uuid4())
            ,
        ), partner_id=partner_id)

    async def create_stage(
        self,
        stage_data,
        partner_id,
        order_chain_id,
    ):
        try:
            order = await self.create_order(
                order_data=stage_data['order'], partner_id=partner_id
            )
        except (
            models.EntityDoesNotExist,
            models.OrderEntitiesError,
            models.OrderReceiverIINNotProvided,
            models.NotDistributionOrdersError,
            models.InvalidPointCoords,
            models.PartnerNotFound,
            models.ProfileNotFound,
            models.OrderAlreadyHaveCourierError,
            models.OrderAddressNotFound,
            models.ItemNotFound
        ) as e:
            raise exceptions.HTTPBadRequestException(str(e)) from e

        schema = OrderChainStageCreateDto(
            order_chain_id=order_chain_id,
            order_id=order.id,
            **stage_data
        )
        return await self.order_chain_stage_repo.create(schema)

    @atomic('default')
    async def create_order_chain(
        self, order_chain: OrderChainCreateModel,
    ) -> None:
        order_chain_dict = order_chain.dict()
        sender = order_chain_dict.pop('sender', None)
        receiver = order_chain_dict.pop('receiver', None)
        stages = order_chain_dict.pop('stages', None)

        sender_created = await self.order_chain_sender_repo.create(sender)
        order_chain_dict['sender_id'] = sender_created.id

        receiver_created = await self.order_chain_receiver_repo.create(receiver)
        order_chain_dict['receiver_id'] = receiver_created.id

        order_chain = await self.order_chain_repo.create(
            OrderChainCreateDto(
                **order_chain_dict
            )
        )
        if stages:
            for stage in stages:
                await self.create_stage(
                    stage,
                    partner_id=order_chain_dict.get('partner_id'),
                    order_chain_id=order_chain.id
                )

        order_chain = await self.order_chain_repo.get_by_id(
            default_filter_args=[], entity_id=order_chain.id
        )

        await self.save_history(
            order_chain_id=order_chain.id,
            request_method=RequestMethods.POST,
        )

        return order_chain

    async def get_list_order_chain(
        self, pagination_params, default_filter_args, filter_kwargs
    ):
        return await self.order_chain_repo.get_list(
            pagination_params=pagination_params, default_filter_args=default_filter_args,
            **filter_kwargs.dict(exclude_unset=True, exclude_none=True)
        )

    async def get_one_order_chain(
        self,
        default_filter_args,
        order_chain_id: int,
    ) -> Union[OrderChainGetDto, dict]:
        return await self.order_chain_repo.get_by_id(
            default_filter_args=default_filter_args, entity_id=order_chain_id
        )

    async def delete_order_chain(
        self, default_filter_args, order_chain_id
    ):
        return await self.order_chain_repo.delete(
            default_filter_args=default_filter_args, entity_id=order_chain_id
        )

    @atomic('default')
    async def delete_stage(
        self, default_filter_args, order_chain_id, idx
    ):
        stage = await self.order_chain_stage_repo.get_by_id(
            default_filter_args=default_filter_args, entity_id=idx, order_chain_id=order_chain_id
        )
        if stage:
            await self.order_chain_stage_repo.delete(
                default_filter_args=[], entity_id=idx, order_chain_id=order_chain_id)
            await models.Order.filter(id=stage.order.id).delete()

            await self.save_history(
                order_chain_id=order_chain_id,
                request_method=RequestMethods.DELETE,
                data={'stage_id': stage.id, 'info': 'delete_stage'}
            )

    @atomic('default')
    async def update_order_chain(
        self,
        order_chain_id: int,
        update: OrderChainUpdateModel,
        default_filter_args,
    ) -> None:
        order_chain_dict = update.dict(exclude_unset=True)
        sender = order_chain_dict.pop('sender', None)
        receiver = order_chain_dict.pop('receiver', None)
        stages = order_chain_dict.pop('stages', None)

        order_chain = await self.order_chain_repo.partial_update_from_dict(
            entity_id=order_chain_id, update_dict=order_chain_dict,
            default_filter_args=default_filter_args
        )

        if sender:
            await self.order_chain_sender_repo.partial_update_from_dict(
                entity_id=order_chain.sender_id, update_dict=sender, default_filter_args=[]
            )

        if receiver:
            await self.order_chain_receiver_repo.partial_update_from_dict(
                entity_id=order_chain.receiver_id, update_dict=receiver, default_filter_args=[]
            )

        for stage in stages:
            await self.order_chain_stage_repo.partial_update_from_dict(
                entity_id=stage.pop('id'), update_dict=stage, default_filter_args=[]
            )

        await self.save_history(
            order_chain_id=order_chain_id,
            request_method=RequestMethods.PATCH,
            data=update.dict(exclude_none=True, exclude_unset=True)
        )

    async def order_chain_add_stage(
        self,
        order_chain_id: int,
        stage: OrderChainStageCreateModel,
        default_filter_args,
    ):
        order_chain = await self.order_chain_repo.get_by_id(
            default_filter_args=default_filter_args, entity_id=order_chain_id
        )
        stage_dict = stage.dict(exclude_unset=True, exclude_none=True)
        stage = await self.create_stage(
            stage_dict,
            partner_id=order_chain.partner.id,
            order_chain_id=order_chain.id
        )
        stage = await self.order_chain_stage_repo.get_by_id(default_filter_args=[], entity_id=stage.id)
        await self.save_history(
            order_chain_id=order_chain_id,
            request_method=RequestMethods.PATCH,
            data={'stage_id': stage.id, 'order_chain_id': order_chain.id, 'info': 'add_stage'}
        )

        return stage

    async def create_support_document(
        self,
        image: UploadFile,
        document_number: str,
        comment: str,
        order_chain_stage_id: int,
    ):
        support_document = await self.order_chain_document_repo.create_by_params(
            image=image,
            document_number=document_number,
            order_chain_stage_id=order_chain_stage_id,
            comment=comment
        )

        stage = await self.order_chain_stage_repo.get_by_id(default_filter_args=[], entity_id=order_chain_stage_id)

        await self.save_history(
            order_chain_id=stage.order_chain_id,
            request_method=RequestMethods.PATCH,
            data={
                'stage_id': stage.id, 'order_chain_id': stage.order_chain_id,
                'support_document_id': support_document.id, 'info': 'add_support_document'
            }
        )

        return stage

    async def update_support_document(
        self,
        image: UploadFile,
        document_number: str,
        comment: str,
        default_filter_args,
        entity_id: int
    ):
        support_document = await self.order_chain_document_repo.partial_update_by_params(
            entity_id=entity_id,
            image=image,
            document_number=document_number,
            comment=comment,
            default_filter_args=default_filter_args
        )

        stage = await self.order_chain_stage_repo.get_by_id(
            default_filter_args=[], entity_id=support_document.order_chain_stage_id
        )

        await self.save_history(
            order_chain_id=stage.order_chain_id,
            request_method=RequestMethods.PATCH,
            data={
                'stage_id': stage.id, 'order_chain_id': stage.order_chain_id,
                'support_document_id': support_document.id,
                'data': {
                    'document_number': document_number,
                    'comment': comment,
                    'image': 'yes'
                },
                'info': 'update_support_document'
            }
        )

        return stage

    @atomic('default')
    async def support_document_delete(
        self, default_filter_args, idx
    ):

        support_document = await self.order_chain_document_repo.get_by_id(
            default_filter_args=default_filter_args, entity_id=idx
        )

        stage = await self.order_chain_stage_repo.get_by_id(
            default_filter_args=[], entity_id=support_document.order_chain_stage_id
        )

        await self.order_chain_document_repo.delete(
            default_filter_args, entity_id=idx)

        await self.save_history(
            order_chain_id=stage.order_chain_id,
            request_method=RequestMethods.PATCH,
            data={
                'stage_id': stage.id,
                'order_chain_id': stage.order_chain_id,
                'support_document_id': support_document.id,
                'info': 'delete_support_document'
            }
        )

    async def set_order_chain_done(self, order: models.Order):
        stage = await order.order_chain_stages_set.all().select_related('order_chain').first()
        if stage and stage.is_last:
            if stage.order_chain.status == OrderChainStatus.IN_PROGRESS.value:
                await self.order_chain_repo.partial_update_from_dict(
                    entity_id=stage.order_chain.id,
                    update_dict={'status': OrderChainStatus.DONE.value},
                    default_filter_args=[]
                )

    async def set_order_chain_in_progress(self, order: models.Order):
        stage = await order.order_chain_stages_set.all().select_related('order_chain').first()
        if stage and not stage.is_last:
            if stage.order_chain.status == OrderChainStatus.NEW.value:
                await self.order_chain_repo.partial_update_from_dict(
                    entity_id=stage.order_chain.id,
                    update_dict={'status': OrderChainStatus.IN_PROGRESS.value},
                    default_filter_args=[]
                )

    async def save_history(self, order_chain_id, request_method, data=None):
        order_chain = await self.order_chain_repo.get_by_id([], order_chain_id)
        if hasattr(self, 'user'):
            return await models.history_create(
                schemas.HistoryCreate(
                    initiator_type=InitiatorType.USER,
                    initiator_id=self.user.id,
                    initiator_role=self.user.profile['profile_type'],
                    model_type=HistoryModelName.ORDER_CHAIN,
                    model_id=order_chain_id,
                    action_data=data,
                    request_method=request_method,
                    created_at=order_chain.receiver.city.localtime,
                )
            )
