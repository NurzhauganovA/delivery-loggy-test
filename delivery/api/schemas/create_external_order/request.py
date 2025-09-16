import datetime
from decimal import Decimal
from typing import Optional, Union

from pydantic import BaseModel, constr, StrictInt, root_validator

from api import enums
from api.common import validators


class ExternalOrderCreate(BaseModel):
    city: Optional[str]
    comment: Optional[str]
    delivery_datetime: Optional[datetime.datetime]
    item_id: int
    shipment_point_id: Optional[int]
    receiver_name: Optional[str]
    receiver_phone_number: str
    receiver_iin: Optional[constr(min_length=12, max_length=12)]
    type: enums.OrderType = enums.OrderType.PLANNED
    callbacks: dict
    address: Optional[str]
    latitude: Decimal
    longitude: Decimal
    order_group_id: Optional[StrictInt]
    partner_order_id: str | None

    product_type: Optional[enums.ProductType]
    product_name: str | None
    payload: Optional[Union[dict, list]]

    _v_ri = validators.reuse('receiver_iin')(validators.validate_iin)
    # _v_lat = validators.reuse('latitude', check_fields=False)(validators.validate_latitude)
    # _v_lon = validators.reuse('longitude', check_fields=False)(validators.validate_longitude)
    _v_ddt = validators.reuse('delivery_datetime')(validators.ensure_delivery_datetime_serialized)

    @root_validator
    def city_is_not_required_when_pickup(cls, values: dict) -> dict:
        order_type = values.get('type')
        city = values.get('city')
        if order_type in [enums.OrderType.PLANNED, enums.OrderType.URGENT, enums.OrderType.OPERATIVE]:
            if not city:
                raise ValueError('Заполнение поля город обязательно для заявок плановых и срочных')

        return values