import time
from typing import List
from typing import Optional

import pydantic
from tortoise.contrib.pydantic import PydanticModel

from .. import enums
from .. import schemas
from api.common.schema_base import BaseOutSchema, BaseInSchema


class City(BaseOutSchema, PydanticModel):
    id: int
    name: str | None


class ItemFilter(pydantic.BaseModel):
    partner_id: Optional[int]


class InnerParamCreate(BaseInSchema):
    name: str
    send: bool = False
    document_code: str | None


class InnerParamUpdate(BaseInSchema):
    id: int | None
    name: str
    send: bool = False
    document_code: str | None


class InnerParamGet(BaseOutSchema):
    id: int
    name: str
    send: bool = False
    document_code: str | None


class PostControlConfigCreate(BaseInSchema, PydanticModel):
    name: str
    send: bool = False
    document_code: str | None
    inner_params: List[InnerParamCreate] = []


class PostControlConfigUpdate(BaseInSchema, PydanticModel):
    id: int | None
    name: str
    send: bool = False
    document_code: str | None
    inner_params: List[InnerParamUpdate | None] | None


class PostControlConfigGet(BaseOutSchema):
    id: int
    name: str
    send: bool = False
    document_code: str | None
    inner_params: List[InnerParamGet] = []


# TODO: check if `deliver_in` correctly constrained,
# and check whether important to limit sum
class ItemBase(PydanticModel):
    name: pydantic.constr(strict=True, max_length=255)
    item_type: enums.ItemType
    delivery_time: Optional[pydantic.StrictStr]
    partner_id: Optional[int]
    category_id: Optional[int]
    delivery_type: Optional[List[enums.OrderType]]
    is_delivery_point_exists: pydantic.StrictBool
    message_for_noncall: str | None
    courier_appointed_sms: pydantic.constr(min_length=10) | None
    courier_appointed_sms_on: bool
    days_to_delivery: str | None

    # noinspection PyMethodParameters
    @pydantic.root_validator()
    def validate_sms(cls, values):
        if not values.get('courier_appointed_sms_on', False):
            return values
        if values.get('courier_appointed_sms') is None:
            raise ValueError({'courier_appointed_sms_on': 'Cannot activate sms for client with empty sms'})

        return values

    # noinspection PyMethodParameters
    @pydantic.validator('delivery_time')
    def ensure_delivery_time_is_valid(cls, value: str) -> str:
        if not value:
            return value
        split_value = value.split(':')
        time_format = '%H'
        hour = split_value[0]
        minutes = ''

        if len(split_value) == 2:
            if not hour:
                time_format = '%M'
            elif any(split_value):
                time_format += ':%M'

            minutes = split_value[1]

        try:
            time.strptime(value.strip(':'), time_format)

            return f'{hour:0>2}:{minutes:0<2}'
        except ValueError as e:
            raise e


class Item(ItemBase):
    pass


class ItemCreate(Item):
    shipment_points: Optional[List[int]]
    deliverygraphs: pydantic.conlist(int, min_items=1)
    postcontrol_configs: List[PostControlConfigCreate] = []
    cities: Optional[List[int]]
    distribute: Optional[bool] = False
    accepted_delivery_statuses: List[enums.OrderDeliveryStatus] | None

    class Config:
        schema_extra = {
            'example': {
                'city_id': 2,
                'delivery_time': '5:00',
                'delivery_type': ['urgent', 'planned'],
                'deliverygraphs': [1, 2],
                'is_delivery_point_exists': True,
                'item_type': 'document',
                'name': 'product23',
                'partner_id': 1,
                'shipment_points': [1],
                'cities': [1, 2],
                'message_for_noncall': 'some message...'
            },
        }


class ItemUpdate(Item):
    cities: Optional[List[int]]
    postcontrol_configs: List[PostControlConfigUpdate] = []
    deliverygraphs: List[int]
    shipment_points: Optional[List[int]]
    postcontrol_configs: List[PostControlConfigUpdate]


class ItemPartialUpdate(pydantic.BaseModel):
    name: pydantic.constr(strict=True, max_length=255) | None
    item_type: enums.ItemType | None
    postcontrol_configs: List[PostControlConfigUpdate] | None
    delivery_time: Optional[pydantic.StrictStr]
    partner_id: Optional[int]
    category_id: Optional[int]
    delivery_type: Optional[List[enums.OrderType]]
    is_delivery_point_exists: pydantic.StrictBool | None
    message_for_noncall: str | None
    courier_appointed_sms: pydantic.constr(min_length=10) | None
    courier_appointed_sms_on: bool | None
    days_to_delivery: str | None
    cities: Optional[List[int]]
    deliverygraphs: List[int] | None
    shipment_points: Optional[List[int]] | None
    distribute: Optional[bool]
    accepted_delivery_statuses: Optional[List[enums.OrderDeliveryStatus]]


class PartnerGetForItem(BaseOutSchema):
    id: int
    name: str


class ItemGet(Item, BaseOutSchema):
    id: int
    name: str | None
    category: Optional[dict]
    partner: PartnerGetForItem = None
    postcontrol_configs: List[PostControlConfigGet] = []
    postcontrol_cancellation_configs: List[PostControlConfigGet] = []
    deliverygraphs: List[schemas.DeliveryGraphGet]
    cities: List[City]
    has_postcontrol: bool
    distribute: Optional[bool]
    accepted_delivery_statuses: List[enums.OrderDeliveryStatus] | None

    class Config:
        orm_mode = True
        use_enum_values = True
        schema_extra = {
            'example': {
                'name': 'Kaspi Gold',
                'item_type': 'document',
                'delivery_time': None,
                'partner_id': 1,
                'category_id': None,
                'deliverygraph_id': 2,
                'delivery_type': ['urgent', 'planned'],
                'is_delivery_point_exists': True,
                'city_id': 2,
                'shipment_points': [
                    {
                        'name': 'test2',
                        'place_id': 1,
                    },
                ],
                'id': 19,
                'message_for_noncall': 'some message...'
            },
        }


class ItemShipmentPointBase(pydantic.BaseModel):
    item_id: pydantic.StrictInt
    shipment_point_id: pydantic.StrictInt


class ItemShipmentPointCreate(ItemShipmentPointBase):
    pass


class ItemCitiesBase(pydantic.BaseModel):
    item_id: pydantic.StrictInt
    city_id: pydantic.StrictInt


class ItemCitiesCreate(ItemCitiesBase):
    pass


class ItemInternal(Item):
    cities: List[int]


class ItemShipmentPointsInternal(ItemShipmentPointBase):
    pass


class ItemIDsList(pydantic.BaseModel):
    items: List[pydantic.StrictInt]

    class Config:
        schema_extra = {
            'example': {
                'items': [1, 2, 3],
            },
        }
