import asyncio
import json
import typing
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List
from typing import Optional

import pydantic
from pydantic import BaseModel, validator
from tortoise.contrib.pydantic import PydanticModel

from .. import enums


class FeedbackReasonBase(pydantic.BaseModel):
    name: pydantic.constr(strict=True, max_length=300)
    is_tag: bool = False
    value: typing.Dict[int, int]

    @pydantic.validator('value')
    def validate_value(cls, value):
        if not value:
            raise ValueError(
                'value must contain at least one rate-score pair'
            )
        for k, v in value.items():
            if k < 4:
                if v > 0:
                    raise ValueError(
                        'score must be negative integer in low rate reasons',
                    )
            if k > 4:
                if v < 0:
                    raise ValueError(
                        'score must be positive integer in high rate reasons',
                    )

        return value


class FeedbackReasonGet(pydantic.BaseModel):
    id: int
    name: str
    is_tag: bool
    value: dict

    @pydantic.validator('value', pre=True)
    def validate_value(cls, value):
        if isinstance(value, str):
            value = json.loads(value)
        return value

    class Config:
        orm_mode = True


class FeedbackReasonRestrictedGet(pydantic.BaseModel):
    id: int
    name: str


class FeedbackReasonCreate(FeedbackReasonBase):
    pass


class FeedbackReasonUpdate(FeedbackReasonBase):
    pass


class Item(BaseModel):
    name: str


class User(BaseModel):
    phone_number: str
    first_name: str
    middle_name: Optional[str]
    last_name: str


class Category(BaseModel):
    name: str


class Courier(BaseModel):
    user: User
    rate: Optional[int]
    category: Optional[Category]

    class Config:
        orm_mode = True


class CourierList(BaseModel):
    user: User

    class Config:
        orm_mode = True


class Partner(PydanticModel):
    name: Optional[str]


class City(BaseModel):
    id: int
    name: str


class Order(BaseModel):
    id: int
    receiver_name: typing.Optional[str]
    receiver_phone_number: str
    item: Item
    city: City
    courier: Optional[Courier]
    partner: Partner

    class Config:
        orm_mode = True


class OrderList(BaseModel):
    item: Item
    courier: Optional[CourierList]

    class Config:
        orm_mode = True


class FeedbackBase(pydantic.BaseModel):
    rate: pydantic.conint(ge=1, le=5)
    comment: Optional[str]


class FeedbackGet(FeedbackBase):
    id: int
    final_score: int
    author_full_name: typing.Optional[str]
    author_phone: typing.Optional[str]
    author_role: typing.Optional[enums.AuthorsFeedback]
    created_at: datetime
    reasons: typing.List[FeedbackReasonRestrictedGet] = []
    status: enums.FeedbackStatus
    order: typing.Optional[Order]

    class Config:
        use_enum_values = True
        orm_mode = True


class FeedbackList(FeedbackBase):
    id: int
    status: enums.FeedbackStatus
    created_at: datetime
    order: typing.Optional[OrderList]
    author_full_name: typing.Optional[str]
    author_phone: typing.Optional[str]

    class Config:
        use_enum_values = True
        orm_mode = True


class FeedbackCreateManager(FeedbackBase):
    reasons: pydantic.conlist(int, min_items=1)
    order_id: pydantic.conint(strict=True)


class FeedbackCreateReceiver(FeedbackBase):
    reasons: pydantic.conlist(int, min_items=1)
    order_id: int


class FeedbackUpdateStatus(pydantic.BaseModel):
    status: enums.FeedbackStatus
    final_score: pydantic.conint(strict=True, ge=-1000, le=1000)

    class Config:
        use_enum_values = True

    @pydantic.root_validator(skip_on_failure=True)
    def validate_final_score(cls, values):
        if values['status'] == enums.FeedbackStatus.DECLINED:
            values['final_score'] = 0
        return values
