import typing
from typing import List, Optional

from api.common.schema_base import BaseOutSchema, BaseInSchema
from pydantic import validator


from .common_schemas import OrderChainSender, OrderChainReceiver, OrderChain, OrderChainStage, OrderChainOptional, \
    Partner, SupportDocument
from ..enums import OrderChainStatus
from ...city.schemas import CityGet


# Support document
class SupportDocumentCreateDto(SupportDocument, BaseInSchema):
    order_chain_stage_id: int


class SupportDocumentGetDto(SupportDocument, BaseOutSchema):
    order_chain_stage_id: int


# Partner
class PartnerDto(Partner, BaseOutSchema):
    id: int


# Courier
class UserDto(BaseOutSchema):
    first_name: typing.Optional[str]
    last_name: typing.Optional[str]
    phone_number: str


class CourierDto(BaseOutSchema):
    user: UserDto


# Order
class StageOrderGetDto(BaseOutSchema):
    id: int
    current_status: dict
    delivery_status: dict
    courier: CourierDto | None


# Sender
class OrderChainSenderGetDto(OrderChainSender, BaseOutSchema):
    id: int
    city: CityGet


class OrderChainSenderCreateDto(OrderChainSender, BaseInSchema):
    ...


# Receiver
class OrderChainReceiverGetDto(OrderChainReceiver, BaseOutSchema):
    id: int
    city: CityGet


class OrderChainReceiverCreateDto(OrderChainReceiver, BaseInSchema):
    ...


# Stage
class OrderChainStageGetDto(BaseOutSchema, OrderChainStage):
    id: int
    order: StageOrderGetDto
    support_documents: Optional[List[SupportDocumentGetDto]]
    order_chain_id: int


class OrderChainStageCreateDto(OrderChainStage, BaseInSchema):
    order_id: int
    order_chain_id: int


# OrderChain
class OrderChainCreateDto(OrderChain, BaseInSchema):
    sender_id: int
    receiver_id: int
    partner_id: int


class OrderChainGetDto(OrderChain, BaseOutSchema):
    id: int
    sender: OrderChainSenderGetDto
    receiver: OrderChainReceiverGetDto
    stages: List[OrderChainStageGetDto]
    partner: PartnerDto
    status: OrderChainStatus

    @validator("stages", pre=True)
    def get_all_stages(cls, v: list) -> object:
        return list(v)

    class Config:
        orm_mode = True


class OrderChainUpdateDto(OrderChainOptional, BaseInSchema):
    pass
