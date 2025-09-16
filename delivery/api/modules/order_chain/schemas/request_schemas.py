from typing import Optional, List

from pydantic import StrictInt, validator

from .dto_schemas import StageOrderGetDto
from ..enums import StageType, OrderChainStatus
from api.common.schema_base import BaseFilterSchema


from .common_schemas import (
    OrderChain, OrderChainReceiver, OrderChainSender, OrderChainStage, StageOrderCreate, OrderChainOptional,
    OrderChainSenderOptional, OrderChainReceiverOptional, OrderChainStageOptional, Partner, SupportDocument
)
from ...city.schemas import CityGet


# Support document
class SupportDocumentCreateModel(SupportDocument):
    order_chain_stage_id: int


class SupportDocumentGetModel(SupportDocument):
    pass


# Partner
class PartnerGetModel(Partner):
    id: int

    class Config:
        orm_mode = True


# Receiver
class OrderChainReceiverGetModel(OrderChainReceiver):
    id: StrictInt
    city: CityGet

    class Config:
        orm_mode = True


class OrderChainReceiverCreateModel(OrderChainReceiver):
    pass


class OrderChainReceiverUpdateModel(OrderChainReceiverOptional):
    pass


# Sender
class OrderChainSenderGetModel(OrderChainSender):
    id: StrictInt
    city: CityGet

    class Config:
        orm_mode = True


class OrderChainSenderCreateModel(OrderChainSender):
    pass


class OrderChainSenderUpdateModel(OrderChainSenderOptional):
    pass


# Stage

class OrderChainStageCreateModel(OrderChainStage):
    order: StageOrderCreate


class OrderChainStageGetModel(OrderChainStage):
    id: int
    type: StageType
    order: Optional[StageOrderGetDto]
    support_documents: Optional[List[SupportDocumentGetModel]]
    position: int

    class Config:
        orm_mode = True


class OrderChainStageUpdateModel(OrderChainStageOptional):
    id: int


# OrderChain
class OrderChainCreateModel(OrderChain):
    partner_id: int
    sender: OrderChainSenderCreateModel
    receiver: OrderChainReceiverCreateModel
    stages: List[OrderChainStageCreateModel | None]


class OrderChainUpdateModel(OrderChainOptional):
    sender: Optional[OrderChainSenderUpdateModel]
    receiver: Optional[OrderChainReceiverUpdateModel]
    stages: List[OrderChainStageUpdateModel | None]


class OrderChainGetModel(OrderChain):
    id: int
    sender: OrderChainSenderGetModel
    receiver: OrderChainReceiverGetModel
    stages: List[OrderChainStageGetModel]
    partner: PartnerGetModel
    status: OrderChainStatus

    @validator("stages", pre=True)
    def get_all_stages(cls, v: list) -> object:
        return list(v)

    class Config:
        orm_mode = True


class OrderChainFilterModel(BaseFilterSchema):
    pass
