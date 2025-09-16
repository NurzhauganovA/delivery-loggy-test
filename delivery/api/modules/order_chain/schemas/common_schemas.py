from decimal import Decimal
from datetime import datetime

from tortoise.contrib.pydantic import PydanticModel

from api.enums import OrderType

from ..enums import OrderChainType, StageType
from pydantic import BaseModel, constr, StrictInt
from typing import Optional

from api.common import validators


class Partner(PydanticModel):
    name: Optional[str]


class MapPoint(BaseModel):
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    address: Optional[constr(strict=True, max_length=255)]
    city_id: Optional[StrictInt]

    _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)


class OrderChainSender(MapPoint):
    name: str
    phone_number: str
    email: Optional[str]


class OrderChainSenderOptional(MapPoint):
    name: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]

class OrderChainReceiver(MapPoint):
    name: str
    phone_number: str
    email: Optional[str]

class OrderChainReceiverOptional(MapPoint):
    name: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]


class PackageParams(BaseModel):
    height: str | None = ""
    width: str | None = ""
    length: str | None = ""
    weight: str | None = ""
    name: str | None = ""
    description: str | None = ""


class OrderChain(BaseModel):
    external_id: str | None
    comment: str | None
    package_params: PackageParams | None
    expected_delivery_datetime: datetime
    deadline_delivery_datetime: datetime
    fact_delivery_datetime: datetime | None
    type: OrderChainType


class OrderChainOptional(BaseModel):
    external_id: str | None
    partner_id: int | None
    comment: str | None
    package_params: PackageParams | None
    expected_delivery_datetime: datetime | None
    deadline_delivery_datetime: datetime | None
    type: OrderChainType | None


class StageOrderCreate(BaseModel):
    city_id: int
    comment: Optional[str]
    delivery_datetime: Optional[datetime]
    item_id: int
    shipment_point_id: Optional[int]
    receiver_name: Optional[str]
    receiver_phone_number: Optional[str]
    receiver_iin: Optional[constr(min_length=12, max_length=12)]
    type: OrderType = OrderType.PLANNED
    callbacks: Optional[dict]
    address: Optional[str]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]

    _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)
    _v_ddt = validators.reuse('delivery_datetime')(validators.ensure_delivery_datetime_serialized)


class OrderStageOrderGet(BaseModel):
    id: int
    current_status: dict


class OrderChainStage(BaseModel):
    type: StageType
    position: int
    is_last: bool


class OrderChainStageOptional(BaseModel):
    type: Optional[StageType]
    position: Optional[int]
    is_last: Optional[bool] | None


class SupportDocument(BaseModel):
    id: int
    document_number: Optional[str]
    comment: Optional[str]
    image: str

