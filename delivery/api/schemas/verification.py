import datetime
import typing

import pydantic

from api.common import validators


class VerificationBase(pydantic.BaseModel):
    confirmed: bool


class VerificationUser(VerificationBase):
    iin: pydantic.constr(min_length=12, max_length=12)


class VerificationPartner(VerificationBase):
    bin: pydantic.constr(min_length=12, max_length=12)


class VerificationCourier(VerificationUser):
    phone_number: str

    _v_phn = validators.reuse('phone_number')(validators.validate_phone)


class VerificationUserRegistrationAddress(pydantic.BaseModel):
    country: typing.Optional[str]
    region: typing.Optional[str]
    city: typing.Optional[str]
    district: typing.Optional[str]
    street: typing.Optional[str]
    building: typing.Optional[str]
    corpus: typing.Optional[str]
    flat: typing.Optional[str]


class VerificationUserBirthPlace(pydantic.BaseModel):
    country: str
    region: typing.Optional[str]
    city: typing.Optional[str]
    district: typing.Optional[str]
    street: typing.Optional[str]
    building: typing.Optional[str]
    corpus: typing.Optional[str]
    flat: typing.Optional[str]


class VerificationUserCapableStatus(pydantic.BaseModel):
    is_capable: typing.Optional[bool]
    registration_date: typing.Optional[datetime.date]
    registration_end_date: typing.Optional[datetime.date]
    number: typing.Optional[str]
    assigned_by: typing.Optional[str]

    _v_rd_red = validators.reuse(
        'registration_date',
        'registration_end_date',
    )(validators.ensure_date_has_valid_type)


class VerificationUserDisappearStatus(pydantic.BaseModel):
    is_disappearead: typing.Optional[bool]
    registration_date: typing.Optional[datetime.date]
    registration_end_date: typing.Optional[datetime.date]
    assigned_by: typing.Optional[str]
    number: typing.Optional[str]

    _v_rd_red = validators.reuse(
        'registration_date',
        'registration_end_date',
    )(validators.ensure_date_has_valid_type)


class VerificationPartnerShipmentPoints(pydantic.BaseModel):
    RKA: typing.Optional[str]
    ZIP: typing.Optional[str]
    KATO: typing.Optional[str]
    ATE: typing.Optional[str]
    geonim_code: typing.Optional[str]
    district: typing.Optional[str]
    region: typing.Optional[str]
    rural: typing.Optional[str]
    city: str
    street: typing.Optional[str]
    building_type: typing.Optional[str]
    building_number: typing.Optional[str]
    block: typing.Optional[str]
    corpus: typing.Optional[str]
    room_type: typing.Optional[str]
    appartment_number: typing.Optional[str]
    office_number: typing.Optional[str]


class VerificationPartnerActivity(pydantic.BaseModel):
    main: bool
    OKED: typing.Optional[str]
    activity_name: str


class VerificationPartnerLiquidation(pydantic.BaseModel):
    reason: typing.Optional[str]
    type: typing.Optional[str]
    decision_date: typing.Optional[datetime.date]
    registration_date: typing.Optional[datetime.date]
    reorganization_type: typing.Optional[str]

    _v_rd_dd = validators.reuse(
        'registration_date',
        'decision_date',
    )(validators.ensure_date_has_valid_type)


class VerificationUserGet(pydantic.BaseModel):
    first_name: str
    last_name: str
    patronymic: typing.Optional[str]
    birth_date: str
    citizenship: str
    nationality: str
    gender: str
    birth_place: VerificationUserBirthPlace
    registration_address: typing.Optional[VerificationUserRegistrationAddress]
    capable_status: typing.Optional[VerificationUserCapableStatus]
    dissapear_status: typing.Optional[VerificationUserDisappearStatus]


class VerificationPartnerGet(pydantic.BaseModel):
    bin: str
    credentials: typing.Optional[dict]
