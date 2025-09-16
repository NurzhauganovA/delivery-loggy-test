import datetime
import decimal
import typing

import email_validator
import pydantic
from tortoise.contrib.pydantic import PydanticModel

from .. import enums


from .shipment_point import PartnerShipmentPointGet
from api.common import schema_base
from api.common import validators
from ..common.schema_base import BaseOutSchema


class JSONSerializer(pydantic.BaseModel):
    @pydantic.root_validator(skip_on_failure=True)
    def ensure_datetime_string_converted(cls, values: dict) -> dict:
        registration_date = values.get('registration_date')
        if registration_date and isinstance(registration_date, datetime.datetime):
            values['registration_date'] = registration_date.isoformat()

        return values


class Identifier(pydantic.BaseModel):
    identifier: typing.Optional[pydantic.constr(strict=True, min_length=12, max_length=12)]
    type: enums.PartnerType

    # noinspection PyMethodParameters
    @pydantic.root_validator()
    def ensure_identifier_is_valid(cls, values: dict) -> dict:
        identifier = values.get('identifier')
        type = values.get('type')
        if type is None:
            return values
        if identifier:
            if type in [enums.PartnerType.IP.value, enums.PartnerType.FL.value]:
                if not identifier.isdigit():
                    raise ValueError('IIN must contain digits only')

                w1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
                w2 = [3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 2]
                check_sum = validators.multiply(identifier, w1) % 11
                if check_sum == 10:
                    check_sum = validators.multiply(identifier, w2) % 11
                if check_sum != int(identifier[-1]):
                    raise ValueError('IIN signature is incorrect')
                if not identifier:
                    raise ValueError('If type of partner is ip or fl IIN identifier is required')
            else:
                bin = validators.ensure_bin_is_valid(identifier)
                if not bin:
                    raise ValueError('If type of partner is too BIN identifier is required')
        return values


class Email(pydantic.BaseModel):
    email: typing.Optional[pydantic.constr(strict=True, max_length=64)]

    @pydantic.validator('email')
    def ensure_email_is_valid(cls, email: str) -> str:
        if email:
            if email_validator.validate_email(email):
                return email

            raise ValueError('Email is not valid')


class CityGetForPartner(BaseOutSchema, PydanticModel):
    id: int
    name: str | None
    country_id: int
    timezone: str | None
    latitude: decimal.Decimal | None
    longitude: decimal.Decimal | None


class PartnerBase(BaseOutSchema, PydanticModel):
    email: typing.Optional[pydantic.constr(strict=True, max_length=64)]
    name: typing.Optional[pydantic.constr(strict=False, max_length=255)]
    start_work_hour: typing.Optional[pydantic.constr(min_length=5, max_length=5, strict=True)]
    end_work_hour: typing.Optional[pydantic.constr(min_length=5, max_length=5, strict=True)]
    activity_name_ru: typing.Optional[pydantic.constr(strict=True, max_length=255)]
    address: typing.Optional[pydantic.constr(strict=True, max_length=255)]
    affiliated: typing.Optional[bool]
    article: typing.Optional[pydantic.constr(strict=True, max_length=64)]
    is_commerce: typing.Optional[bool]
    consent_confirmed: typing.Optional[bool]
    is_government: typing.Optional[bool]
    is_international: typing.Optional[bool]
    registration_date: typing.Optional[datetime.datetime]
    liq_decision_date: typing.Optional[datetime.date]
    liq_date: typing.Optional[datetime.date]

    _v_svh = validators.reuse('start_work_hour')(validators.ensure_work_time_is_valid)
    _v_evh = validators.reuse('end_work_hour')(validators.ensure_work_time_is_valid)


class PartnerFetched(PartnerBase, JSONSerializer):
    cities: typing.List[int] | None
    partner_in: typing.Optional[typing.Union[list, dict]] | None
    leader_data: typing.Optional[typing.Dict] | None


class Partner(Identifier, PartnerBase, JSONSerializer):
    cities: typing.List[CityGetForPartner] | None
    courier_partner_id: typing.Optional[pydantic.conint(strict=False)]
    credentials: typing.Optional[dict]
    type: enums.PartnerType


class PartnerCreate(Identifier):
    identifier: typing.Optional[pydantic.constr(strict=True, min_length=12, max_length=12)]
    type: enums.PartnerType
    credentials: typing.Optional[PartnerFetched]


class DeliveryServiceCreate(Identifier):
    service_manager_phone_number: typing.Optional[str]
    name_ru: typing.Optional[
        pydantic.constr(strict=True, max_length=255)
    ]

    @pydantic.validator('name_ru', 'type', check_fields=False)
    def ensure_name_ru_is_valid(cls, field_value, values, **kwargs) -> str:
        type = values.get('type', None)
        if type in [enums.PartnerType.IP.value, enums.PartnerType.FL.value] and not field_value:
            raise ValueError('name_ru field is required!')

        return field_value

    _v_phn = validators.reuse('service_manager_phone_number')(validators.validate_phone)


class PartnerUpdate(schema_base.partial(PartnerBase), JSONSerializer, schema_base.partial(Identifier)):
    cities: typing.List[int] | None
    courier_partner_id: typing.Optional[pydantic.conint(strict=False)]
    type: enums.PartnerType | None

    class Config:
        extra = 'allow'


class PartnerGet(PartnerBase, PydanticModel):
    id: pydantic.conint(strict=True)
    registration_date: typing.Optional[datetime.datetime]
    shipment_points: typing.Optional[typing.List[PartnerShipmentPointGet]]
    quantity_products: typing.Optional[int]
    quantity_managers: typing.Optional[int]
    quantity_orders: typing.Optional[int]
    quantity_couriers: typing.Optional[int]
    leader_data: typing.Optional[dict]
    history: typing.Optional[list]
    credentials: typing.Optional[dict]
    identifier: typing.Optional[pydantic.constr(strict=True, min_length=12, max_length=12)]
    type: enums.PartnerType
    courier_partner_id: typing.Optional[int]
    cities: typing.List[CityGetForPartner] | None


class PartnerGetItem(PydanticModel):
    id: int
    name: typing.Optional[pydantic.constr(strict=False, max_length=256)]


class PartnerDeleteBulk(pydantic.BaseModel):
    partner_id_list: typing.List[int]

    class Config:
        schema_extra = {
            'example': {
                'partner_id_list': [1, 3, 5, 6, 29, 3953],
            },
        }


class PartnerInternal(Partner):
    courier_partner_id: typing.Optional[int]
