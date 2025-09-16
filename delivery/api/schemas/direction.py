import typing
from typing import Optional

from . import place


class Direction(place.Coordinates):
    order_id: Optional[int]
    position: Optional[int]
    delivery_status: dict
    type: Optional[str]


class DirectionGet(Direction):
    receiver_name: typing.Optional[str]
    receiver_phone_number: str
    address: str

