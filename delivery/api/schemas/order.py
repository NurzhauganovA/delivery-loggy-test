import datetime
import typing
from decimal import Decimal
from typing import List
from typing import (
    Optional,
    Union,
)

import pydantic
from fastapi import Query
from loguru import logger
from pydantic import(
    BaseModel,
    conset,
    Field,
    conint,
    validator,
    StrictBool,
    StrictInt,
    StrictStr,
    conlist,
    constr,
    root_validator,
)
from tortoise.contrib.pydantic import PydanticModel

from .deliverygraph import(
    DeliveryGraphGet,
    DeliveryGraphGetV2,
)
from api import enums, exceptions
from api.common import validators
from ..common.schema_base import BaseOutSchema
from ..domain.pan import Pan
from ..enums import PostControlType



class Area(BaseModel):
    id: int
    slug: str


class City(BaseOutSchema, PydanticModel):
    id: int
    name: str | None
    timezone: str = 'UTC'


class Item(BaseOutSchema, PydanticModel):
    name: str
    has_postcontrol: Optional[bool]
    message_for_noncall: str | None

    class Config:
        orm_mode = True


class PostcontrolDocumentGet(BaseModel):
    id: int
    image: str
    resolution: enums.PostControlResolution
    comment: str | None

    class Config:
        use_enum_values = True


class PostControlGet(BaseModel):
    id: int
    order_id: int
    image: str | None
    config_id: int | None
    type: PostControlType

    class Config:
        use_enum_values = True
        orm_mode = True


class InnerParamGet(BaseOutSchema):
    id: int
    name: str
    send: bool = False
    document_code: str | None
    postcontrol_documents: List[PostcontrolDocumentGet] = []


class OrderPostcontrolConfigGet(BaseModel):
    id: int
    name: str
    inner_params: List[InnerParamGet] = []
    postcontrol_documents: List[PostcontrolDocumentGet] = []

    class Config:
        orm_mode = True


class ItemGet(Item):
    upload_from_gallery: bool
    postcontrol_configs: List[OrderPostcontrolConfigGet] = []
    postcontrol_cancellation_configs: List[OrderPostcontrolConfigGet] = []
    accepted_delivery_statuses: List[str] | None


class ItemV2(BaseOutSchema, PydanticModel):
    name: str | None
    has_postcontrol: Optional[bool]


class ItemGetV2(BaseOutSchema, PydanticModel):
    name: str | None
    has_postcontrol: bool = False
    message_for_noncall: str | None
    upload_from_gallery: bool
    postcontrol_configs: List[OrderPostcontrolConfigGet] = []
    postcontrol_cancellation_configs: List[OrderPostcontrolConfigGet] = []
    accepted_delivery_statuses: List[str] | None = []


class User(BaseModel):
    id: int
    phone_number: str
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]


class Courier(BaseModel):
    id: int
    user: User

    class Config:
        orm_mode = True


class StatusChildItem(BaseOutSchema, PydanticModel):
    id: StrictInt
    name: typing.Optional[StrictStr]


class Status(BaseOutSchema, PydanticModel):
    name: StrictStr | None
    is_optional: StrictBool
    icon: StrictStr
    partner_id: Optional[StrictInt]
    after: List[StatusChildItem] | None = []


class StatusCreate(Status):
    pass


class StatusGet(Status):
    id: StrictInt
    slug: StrictStr


class StatusGetV2(BaseOutSchema, PydanticModel):
    id: int
    name: str | None
    icon: str
    slug: str


class StatusBulkCreate(BaseModel):
    __root__: List[Status]


class StatusUpdate(Status):
    pass


class AfterInternal(BaseModel):
    id: int
    name: str


class StatusInternal(Status):
    id: int
    slug: str
    after: List[AfterInternal]


class DeliveryStatusExternal(BaseModel):
    status: enums.OrderDeliveryStatus | None
    status_datetime: str
    comment: Optional[str]


class DeliveryStatus(BaseModel):
    status: Optional[enums.OrderDeliveryStatus] | None
    datetime: Optional[str]
    comment: Optional[str]
    reason: Optional[str]

    class Config:
        use_enum_values = True

    @root_validator(skip_on_failure=True)
    def ensure_datetime_serialized(cls, values: dict) -> dict:
        delivery_datetime = values.get('datetime')
        if delivery_datetime and isinstance(delivery_datetime, str):
            datetime.datetime.fromisoformat(
                delivery_datetime,
            )

        return values

    @root_validator
    def validate_dependent_fields(cls, values: dict) -> dict:
        status = values.get('status')
        if not status or status not in {
            enums.OrderDeliveryStatus.CANCELLED,
            enums.OrderDeliveryStatus.REQUESTED_TO_CANCEL,
            enums.OrderDeliveryStatus.POSTPONED,
            enums.OrderDeliveryStatus.NONCALL,
            enums.OrderDeliveryStatus.CANCELED_AT_CLIENT,
            enums.OrderDeliveryStatus.RESCHEDULED,
            enums.OrderDeliveryStatus.BEING_FINALIZED_AT_CS,
            enums.OrderDeliveryStatus.BEING_FINALIZED_ON_CANCEL,
        }:
            values['datetime'] = None
            values['reason'] = None
        elif status == enums.OrderDeliveryStatus.NONCALL:
            values['reason'] = None
            values['datetime'] = None
        elif status in (enums.OrderDeliveryStatus.CANCELLED,
                        enums.OrderDeliveryStatus.CANCELED_AT_CLIENT,
                        enums.OrderDeliveryStatus.RESCHEDULED):
            if not values.get('reason'):
                raise ValueError(
                    'reason is required when order was canceled',
                )
        elif status == enums.OrderDeliveryStatus.POSTPONED:
            values['reason'] = None

        return values


class OrderStatus(BaseModel):
    order_id: int
    created_at: datetime.datetime


class OrderStatusesGet(OrderStatus):
    statuses: List[Status]


class OrderStatusGet(OrderStatus):
    status: StatusGet
    delivery_status: DeliveryStatus


class OrderBase(BaseOutSchema, PydanticModel):
    city_id: Optional[StrictInt]
    partner_id: StrictInt
    partner_order_id: constr(min_length=1) | None
    main_order_id: Optional[StrictInt]
    item_id: StrictInt
    type: enums.OrderType
    delivery_datetime: Optional[datetime.datetime]
    delivery_status: Optional[DeliveryStatus]
    receiver_iin: Optional[constr(min_length=12, max_length=12)]
    receiver_name: typing.Optional[constr(max_length=255)]
    receiver_phone_number: str
    has_receiver_feedback: Optional[bool]
    comment: Optional[constr(max_length=255)]
    area_id: Optional[StrictInt]
    created_by: enums.CreatedType
    order_group_id: Optional[StrictInt]
    revised: Optional[bool]

    class Config:
        allow_enum_values = True


class OrderInBase(BaseModel):
    receiver_phone_number: str
    receiver_iin: constr(min_length=12, max_length=12) | None
    receiver_name: constr(max_length=255) | None
    comment: constr(max_length=255) | None
    idn: str | None = None
    manager: constr(min_length=2, max_length=255) | None = None

    _v_ri = validators.reuse('receiver_iin')(validators.validate_iin)
    _v_phn = validators.reuse('receiver_phone_number')(validators.validate_phone)

    class Config:
        allow_enum_values = True


class OrderOutBaseV2(BaseOutSchema, PydanticModel):
    id: int
    type: enums.OrderType
    delivery_datetime: datetime.datetime | None
    delivery_status: DeliveryStatus | None
    receiver_iin: str | None
    receiver_name: str | None
    receiver_phone_number: str
    comment: str | None
    created_by: enums.CreatedType
    idn: str | None = None


class Order(OrderBase):
    _v_ddt = validators.reuse('delivery_datetime')(validators.ensure_delivery_datetime_serialized)


class OrderAddress(BaseModel):
    position: StrictInt
    type: enums.AddressType


class OrderAddressCreate(OrderAddress):
    place_id: StrictInt


class OrderAddressUpdate(OrderAddressCreate):
    id: StrictInt


class OrderCreate(Order):
    courier_id: Optional[StrictInt]
    addresses: List[OrderAddressCreate] | None
    distribute_now: bool
    idn: str | None = None
    manager: constr(min_length=2, max_length=255) | None = None

    _v_ri = validators.reuse('receiver_iin')(validators.validate_iin)

    # noinspection PyMethodParameters
    @pydantic.root_validator(skip_on_failure=True)
    def validate_object(cls, values: dict) -> dict:

        #  pickup related validations
        if values['type'] != enums.OrderType.PICKUP:
            if not values.get('addresses'):
                raise ValueError('Address is required')
        else:
            if values.get('courier_id'):
                raise ValueError('Can not assign courier on pickup orders')
            if values.get('distribute_now'):
                raise ValueError('Can not distribute a pickup order')

        return values


class DeliveryPointCreate(BaseModel):
    latitude: Decimal
    longitude: Decimal
    address: pydantic.constr(strict=True, max_length=255)

    _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)


class DeliveryPointGet(BaseModel):
    id: int
    latitude: Decimal
    longitude: Decimal
    address: pydantic.constr(strict=True, max_length=255)


class ShipmentPointGet(BaseModel):
    name: str | None
    address: str
    latitude: Decimal
    longitude: Decimal


class OrderCreateV2(OrderInBase):
    city_id: int
    has_receiver_feedback: bool | None
    order_group_id: StrictInt | None
    partner_id: StrictInt
    item_id: StrictInt
    type: enums.OrderType
    partner_order_id: constr(min_length=1) | None
    main_order_id: StrictInt | None
    delivery_datetime: datetime.datetime | None
    courier_id: StrictInt | None
    shipment_point_id: StrictInt | None
    delivery_point: DeliveryPointCreate | None

    product_type: Optional[enums.ProductType]
    product_name: str | None
    payload: Optional[dict]

    _v_ri = validators.reuse('receiver_iin')(validators.validate_iin)

    # noinspection PyMethodParameters
    @pydantic.root_validator(skip_on_failure=True)
    def validate_object(cls, values: dict) -> dict:

        #  pickup related validations
        if values['type'] != enums.OrderType.PICKUP:
            if not values.get('delivery_point'):
                raise ValueError('Delivery point is required')
        else:
            if values.get('courier_id'):
                raise ValueError('Can not assign courier on pickup orders')
        return values


class OrderUpdate(OrderInBase):
    pass


class OrderRestore(BaseModel):
    courier_id: Optional[StrictInt]
    delivery_datetime: Optional[datetime.datetime]
    delivery_status: Optional[DeliveryStatus]


class OrderUpdateStatus(BaseModel):
    status: enums.OrderStatus


class PlaceGet(BaseModel):
    id: int
    address: str
    city_id: Optional[int]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]


class OrderAddressGet(OrderAddress):
    id: StrictInt
    place: PlaceGet

    class Config:
        orm_mode = True


class OrderReschedule(BaseModel):
    delivery_datetime: Optional[datetime.datetime]
    reason: str
    place: Optional[PlaceGet]


class OrderInternal(Order):
    pass


class OrderStatusGetWithDatetime(BaseOutSchema, PydanticModel):
    status: StatusGet
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class OrderStatusGetWithDatetimeV2(BaseModel):
    status: StatusGetV2
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class Partner(BaseOutSchema, PydanticModel):
    id: int
    name: str | None
    article: str
    courier_partner_id: Optional[int]


class Postcontrol(BaseModel):
    id: int
    image: str
    type: str
    resolution: Optional[str]
    comment: Optional[str]


class OrderList(Order):
    id: int
    order_chain_stages: Optional[List[dict]]
    initial_delivery_datetime: datetime.datetime | None
    courier_id: Optional[StrictInt]
    created_at: datetime.datetime
    position: Optional[int]
    courier: Optional[Courier]
    city: Optional[City]
    area: Optional[Area]
    partner: Optional[Partner]
    shipment_point_id: int | None
    delivery_point_id: int | None
    addresses: Optional[List[OrderAddressGet]]
    item: Item
    deliverygraph: Optional[DeliveryGraphGet]
    statuses: List[OrderStatusGetWithDatetime]

    class Config:
        orm_mode = True


class Product(BaseOutSchema):
    id: int
    type: str
    name: str | None
    attributes: Union[dict, list]

    @root_validator
    def mask_pan(cls, values):
        """
            Если у продукта с типом card есть pan в attributes,
            то наложим маску
        """
        product_type = values.get("type")

        if product_type == "card":
            current_pan = values.get("attributes", {}).get("pan")
            if current_pan:
                pan = Pan(value=current_pan)
                values["attributes"]["pan"] = pan.get_masked()

        return values


class ProductList(BaseOutSchema):
    name: str | None


class OrderListV2(OrderOutBaseV2):
    initial_delivery_datetime: datetime.datetime | None
    created_at: datetime.datetime
    courier: Courier | None
    city: City | None
    area: Area | None
    partner: Partner | None
    shipment_point: ShipmentPointGet | None
    delivery_point: DeliveryPointGet | None
    item: ItemV2
    deliverygraph_step_count: int = 0
    current_status_position: int | None
    current_status: StatusGetV2 | None
    manager: str | None = None
    product: Product | None = None


class OrderGet(OrderList):
    courier_id: Optional[StrictInt]
    item: ItemGet
    last_otp: datetime.datetime | None
    statuses: List[OrderStatusGetWithDatetimeV2]
    current_status_id: int | None = None



class OrderListMobile(OrderList):
    courier_id: Optional[StrictInt]
    item: ItemGet
    last_otp: datetime.datetime | None
    statuses: List[OrderStatusGetWithDatetimeV2]
    current_status_id: int | None = None
    product: ProductList | None


class OrderGetV1(OrderList):
    actual_delivery_datetime: datetime.datetime | None
    courier_id: Optional[StrictInt]
    item: ItemGet
    last_otp: datetime.datetime | None
    statuses: List[OrderStatusGetWithDatetimeV2]
    current_status_id: int | None = None
    product: Product | None


class OrderGetV2(OrderListV2):
    item: ItemGetV2
    deliverygraph: DeliveryGraphGetV2 | None
    statuses: List[OrderStatusGetWithDatetime]
    last_otp: datetime.datetime | None
    actual_delivery_datetime: datetime.datetime | None
    product: Product | None
    courier_assigned_at: datetime.datetime | None


class OrdersCount(BaseModel):
    count: Optional[int]


class OrderPartnerGet(BaseModel):
    article: Optional[StrictStr]
    name: StrictStr
    id: StrictInt


class OrderFilterParamsBase(BaseModel):
    courier_id: Optional[int]
    order_group_id: Optional[int]
    delivery_datetime__gte: Optional[datetime.datetime]
    delivery_datetime__lte: Optional[datetime.datetime]
    search_type: Optional[enums.OrderSearchType]
    search: Optional[str]
    position: Optional[int]
    archived: Optional[bool] = Field(Query(False))
    created_by: Optional[enums.CreatedType]
    current_status: Optional[int]
    current_status__in: List[int] | None = Field(Query(None))
    current_status_slug: Optional[enums.StatusSlug]
    current_status_slug__in: List[enums.StatusSlug] | None = Field(Query(None))
    city_id__in: List[int] | None = Field(Query(None))
    item_id__in: List[int] | None = Field(Query(None))
    delivery_status: conset(enums.OrderDeliveryStatusQuery) | None = Field(Query(None))
    exclude_order_status_ids: List[int] | None = Field(Query(None))

    class Config:
        use_enum_values = True


class OrderFilterParams(OrderFilterParamsBase):
    address_set__place__latitude__isnull: bool | None
    address_set__place__longitude__isnull: bool | None


class OrderFilterParamsV2(OrderFilterParamsBase):
    delivery_point__latitude__isnull: bool | None
    delivery_point__longitude__isnull: bool | None


class Coordinates(BaseModel):
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]

    _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)

    def to_tuple(self):
        return self.latitude, self.longitude


class OrderSmsCode(BaseModel):
    code: str
    code_sent_point: Coordinates | None

    @validator("code")
    def validate_code(cls, v):
        if len(v) != 4:
            raise exceptions.HTTPBadRequestException("Provided code did not match")
        return v


class OrderAddressChange(BaseModel):
    places: List[PlaceGet]
    change_reason: enums.OrderChangeAddressReason
    comment: Optional[str]
    change_type: enums.OrderChangeAddressType
    delivery_datetime: Optional[datetime.datetime]

    class Config:
        use_enum_values = True

    @root_validator
    def validate_dependent_fields(cls, values: dict) -> dict:
        change_type = values.get('change_type')
        if change_type in [
            enums.OrderChangeAddressType.RESTORE,
            enums.OrderChangeAddressType.SAVE_COURIER_NEW_DELIVERY_DATETIME,
            enums.OrderChangeAddressType.NEW_COURIER_NEW_DELIVERY_DATETIME,
        ] and not values.get('delivery_datetime'):
            raise ValueError(
                'delivery_datetime value is required',
            )

        change_reason = values.get('change_reason')

        if (change_reason == enums.OrderChangeAddressReason.INCORRECT_ADDRESS
                and not values.get('comment')):
            raise ValueError(
                'comment value is required',
            )

        return values


class OrderAddressChangeV2(BaseModel):
    city_id: conint(ge=1) | None
    delivery_point: DeliveryPointCreate
    change_reason: enums.OrderChangeAddressReason
    comment: str | None
    change_type: enums.OrderChangeAddressType
    delivery_datetime: datetime.datetime | None

    class Config:
        use_enum_values = True

    @root_validator
    def validate_dependent_fields(cls, values: dict) -> dict:
        change_type = values['change_type']
        if change_type in [
            enums.OrderChangeAddressType.RESTORE,
            enums.OrderChangeAddressType.SAVE_COURIER_NEW_DELIVERY_DATETIME,
            enums.OrderChangeAddressType.NEW_COURIER_NEW_DELIVERY_DATETIME,
        ] and not values.get('delivery_datetime'):
            raise ValueError(
                'delivery_datetime value is required',
            )

        change_reason = values['change_reason']

        if (change_reason == enums.OrderChangeAddressReason.INCORRECT_ADDRESS
                and not values.get('comment')):
            raise ValueError(
                'comment value is required',
            )

        return values


class OrderMassCourierAssign(BaseModel):
    courier_id: int
    orders: conlist(int, min_items=1, unique_items=True)


class OrderMassStatusUpdate(BaseModel):
    delivery_status: Optional[DeliveryStatus] | None
    delivery_datetime: Optional[datetime.datetime]
    orders: conlist(int, min_items=1, unique_items=True)


class OrderPAN(BaseModel):
    pan: constr(max_length=16)
    input_type: enums.InputPanType | None

    @pydantic.validator('pan')
    def validate_pan(cls, value):
        # Validate checksum
        value = value.replace(' ', '').replace('-', '')
        digits = list(map(int, value))
        odd_sum = sum(digits[-1::-2])
        even_sum = sum(sum(divmod(2 * d, 10)) for d in digits[-2::-2])
        checksum = (odd_sum + even_sum) % 10
        if checksum != 0:
            raise ValueError('Invalid PAN')

        logger.info(value)
        return value


class OrderChangeStatus(BaseModel):
    status_id: int
    order_id_list: conlist(int, min_items=1)


class UpdateDeliveryPoint(BaseModel):
    latitude: Decimal
    longitude: Decimal
    address: pydantic.constr(strict=True, max_length=255)


class OrderUpdateDeliveryPoint(BaseModel):
    delivery_point: UpdateDeliveryPoint
    comment: str = None
