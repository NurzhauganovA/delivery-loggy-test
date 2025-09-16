import datetime
import decimal
import typing

import pydantic
from tortoise.contrib.pydantic import PydanticModel

from .country import CityGet
from .. import enums
from api.common import schema_base
from api.common import validators
from ..common.schema_base import BaseOutSchema


class Country(BaseOutSchema):
    id: int
    name: str


class UserCreate(pydantic.BaseModel):
    phone_number: typing.Optional[str]
    iin: typing.Optional[pydantic.constr(strict=True, min_length=12, max_length=12)]
    first_name: typing.Optional[pydantic.constr(max_length=32)]
    last_name: typing.Optional[pydantic.constr(max_length=32)]
    middle_name: typing.Optional[pydantic.constr(max_length=32)]
    credentials: typing.Optional[typing.Dict[str, typing.Any]]
    email: typing.Optional[str]

    _v_phn = validators.reuse('phone_number')(validators.validate_phone)

    @pydantic.validator('email')
    def empty_email_2_none(cls, v):
        if v == '':
            return None
        return v

    class Config:
        extra = 'forbid'


class ProfileBase(pydantic.BaseModel):
    partner_id: int

    class Config:
        extra = 'forbid'


# Replace ProfileOwner
class ProfileOwner(ProfileBase):
    pass


class ProfileOwnerCreate(ProfileOwner):
    pass


class ProfileOwnerUpdate(ProfileOwner):
    pass


class ProfileOwnerGet(ProfileOwner):
    pass


class ProfileOwnerInternal(ProfileOwner):
    pass


class ProfileCourier(ProfileBase):
    city_id: typing.Optional[pydantic.StrictInt]
    category_id: typing.Optional[int]
    at_work: typing.Optional[pydantic.StrictBool]
    start_work_hour: typing.Optional[pydantic.constr(min_length=5, max_length=5)]
    end_work_hour: typing.Optional[pydantic.constr(min_length=5, max_length=5)]
    experience_years: typing.Optional[pydantic.conint(ge=0, le=12)]
    experience_months: typing.Optional[pydantic.conint(ge=0, le=64)]
    schedule: typing.List[enums.Weekday]
    is_identified: typing.Optional[pydantic.StrictBool] = False
    is_biometry_verificated: typing.Optional[pydantic.StrictBool] = False
    register_with_biometry: typing.Optional[pydantic.StrictBool] = False
    iban: typing.Optional[pydantic.constr(max_length=34, min_length=16)]
    item_type: typing.Optional[enums.ItemType]
    transport_type: typing.Optional[enums.TransportType]
    state: typing.Optional[enums.CourierState]
    status: typing.Optional[enums.InviteStatus]
    areas: typing.Optional[list]

    class Config:
        extra = 'forbid'
        use_enum_values = True


class ProfileCourierCreate(ProfileCourier):
    pass


class ProfileCourierUpdate(ProfileCourier):
    pass


class ProfileCourierGet(ProfileCourier):
    orders_delivered_today: int
    average_time_deviation: typing.Optional[int]
    created_at: datetime.datetime


class ProfileCourierInternal(ProfileCourier):
    at_work: pydantic.StrictBool


class StatsBase(pydantic.BaseModel):
    rate: int
    negative_feedbacks: int
    positive_feedbacks: int
    orders: int
    late_delivery: int


class Stats(StatsBase):
    month: typing.Optional[datetime.date]


class StatsCourier(pydantic.BaseModel):
    id: int
    first_name: str
    middle_name: typing.Optional[str]
    last_name: str
    user_id: int
    category_type: typing.Optional[str]
    category_name: typing.Optional[str]


class ProfileCourierStats(pydantic.BaseModel):
    courier: StatsCourier
    rates: typing.List[Stats]
    total: typing.Optional[StatsBase]


class ProfileCourierStatsList(StatsBase):
    courier: StatsCourier


class ProfileDispatcher(ProfileBase):
    pass


class ProfileDispatcherCreate(ProfileDispatcher):
    partners: typing.List[int]


class ProfileDispatcherUpdate(ProfileDispatcher):
    partners: typing.List[int]


class ProfileDispatcherGet(ProfileDispatcher):
    pass


class ProfileDispatcherInternal(ProfileDispatcher):
    pass


class ProfileManager(ProfileBase):
    pass


class ProfileManagerCreate(ProfileManager):
    pass


class ProfileManagerUpdate(ProfileManager):
    pass


class ProfileManagerGet(ProfileManager):
    pass


class ProfileManagerInternal(ProfileManager):
    pass


class ProfileBankManager(ProfileBase):
    pass


class ProfileBankManagerCreate(ProfileBankManager):
    pass


class ProfileBankManagerUpdate(ProfileBankManager):
    pass


class ProfileBankManagerGet(ProfileBankManager):
    pass


class ProfileBankManagerInternal(ProfileBankManager):
    pass


class ProfileServiceManager(ProfileBase):
    pass


class ProfileServiceManagerCreate(ProfileServiceManager):
    pass


class ProfileBranchManager(ProfileBase):
    pass


class ProfileBranchManagerCreate(ProfileBranchManager):
    cities: typing.List[int] | None


class ProfileBranchManagerUpdate(ProfileBranchManager):
    cities: typing.List[int] | None


class ProfileBranchManagerGet(ProfileBranchManager):
    cities: typing.List[CityGet] | list

    class Config:
        orm_mode = True


class ProfileBranchManagerInternal(ProfileBranchManager):
    pass


class Place(pydantic.BaseModel):
    id: int
    address: str
    latitude: float
    longitude: float

    class Config:
        orm_mode = True


class Partner(PydanticModel):
    name: typing.Optional[str]


class ShipmentPointGet(pydantic.BaseModel):
    name: typing.Optional[str]
    partner: Partner
    address: str
    latitude: decimal.Decimal
    longitude: decimal.Decimal

    class Config:
        orm_mode = True


class ProfilePartnerBranchManager(ProfileBase):
    shipment_point_id: int


class ProfilePartnerBranchManagerCreate(ProfilePartnerBranchManager):
    pass


class ProfilePartnerBranchManagerUpdate(ProfilePartnerBranchManager):
    pass


class ProfileServiceManagerUpdate(ProfileServiceManager):
    pass


class ProfileServiceManagerGet(ProfileServiceManager):
    pass


class ProfileServiceManagerInternal(ProfileServiceManager):
    pass


class ProfileSorter(ProfileBase):
    shipment_point_id: int


class ProfileSorterCreate(ProfileSorter):
    pass


class ProfileSorterUpdate(ProfileSorter):
    pass


class ProfileSorterGet(ProfileSorter):
    shipment_point: ShipmentPointGet


class ProfileSupervisor(ProfileBase):
    country_id: int


class ProfileSupervisorCreate(ProfileSupervisor):
    pass

class ProfileSupervisorUpdate(ProfileSupervisor):
    pass

class ProfileSupervisorGet(ProfileSupervisor):
    country: Country


class ProfileSupervisorInternal(ProfileSupervisor):
    pass


class ProfileLogist(ProfileBase):
    country_id: int


class ProfileLogistCreate(ProfileLogist):
    pass

class ProfileLogistUpdate(ProfileLogist):
    pass

class ProfileLogistGet(ProfileLogist):
    country: Country


class ProfileLogistInternal(ProfileLogist):
    pass


class ProfileCallCenterManager(ProfileBase):
    country_id: int


class ProfileCallCenterManagerCreate(ProfileCallCenterManager):
    pass

class ProfileCallCenterManagerUpdate(ProfileCallCenterManager):
    pass

class ProfileCallCenterManagerGet(ProfileCallCenterManager):
    country: Country


class ProfileCallCenterManagerInternal(ProfileCallCenterManager):
    pass


class ProfileGeneralCallCenterManager(ProfileBase):
    pass


class ProfileGeneralCallCenterManagerCreate(ProfileGeneralCallCenterManager):
    pass

class ProfileGeneralCallCenterManagerUpdate(ProfileGeneralCallCenterManager):
    pass

class ProfileGeneralCallCenterManagerGet(ProfileGeneralCallCenterManager):
    pass


class ProfileGeneralCallCenterManagerInternal(ProfileGeneralCallCenterManager):
    pass


class ProfileSupport(ProfileBase):
    pass


class ProfileSupportCreate(ProfileSupport):
    pass

class ProfileSupportUpdate(ProfileSupport):
    pass

class ProfileSupportGet(ProfileSupport):
    pass


class ProfileSupportInternal(ProfileSupport):
    pass


# Make common OneOfProfilesCreateOrUpdate
# in case there won't be any difference
# between both of underlying unions
OneOfProfilesCreate = typing.Union[
    ProfileBranchManagerCreate,
    ProfileCourierCreate,
    ProfileDispatcherCreate,
    ProfileManagerCreate,
    ProfileBankManagerCreate,
    ProfileOwnerCreate,
    ProfilePartnerBranchManagerCreate,
    ProfileServiceManagerCreate,
    ProfileSorterCreate,
    ProfileSupervisorCreate,
    ProfileLogistCreate,
    ProfileCallCenterManagerCreate,
    ProfileGeneralCallCenterManagerCreate,
    ProfileSupportCreate,
]

OneOfProfilesUpdate = typing.Union[
    ProfileBranchManagerUpdate,
    ProfileCourierUpdate,
    ProfileDispatcherUpdate,
    ProfileManagerUpdate,
    ProfileBankManagerUpdate,
    ProfileOwnerUpdate,
    ProfilePartnerBranchManagerUpdate,
    ProfileServiceManagerUpdate,
    ProfileSorterUpdate,
    ProfileSupervisorUpdate,
    ProfileLogistUpdate,
    ProfileCallCenterManagerUpdate,
    ProfileGeneralCallCenterManagerUpdate,
    ProfileSupportUpdate,
]

OneOfProfilesPartialUpdate = typing.Union[
    schema_base.partial(ProfileBranchManagerUpdate),
    schema_base.partial(ProfileCourierUpdate),
    schema_base.partial(ProfileDispatcherUpdate),
    schema_base.partial(ProfileManagerUpdate),
    schema_base.partial(ProfileBankManagerUpdate),
    schema_base.partial(ProfileOwnerUpdate),
    schema_base.partial(ProfilePartnerBranchManagerUpdate),
    schema_base.partial(ProfileServiceManagerUpdate),
    schema_base.partial(ProfileSorterUpdate),
    schema_base.partial(ProfileSupervisorUpdate),
    schema_base.partial(ProfileLogistUpdate),
    schema_base.partial(ProfileCallCenterManagerUpdate),
    schema_base.partial(ProfileGeneralCallCenterManagerUpdate),
    schema_base.partial(ProfileSupportUpdate),
]

OneOfProfilesInternal = typing.Union[
    ProfileCourierInternal,
    ProfileDispatcherInternal,
    ProfileManagerInternal,
    ProfileBankManagerInternal,
    ProfileOwnerInternal,
    ProfileServiceManagerInternal,
    ProfileBranchManagerInternal,
    ProfileSupervisorInternal,
    ProfileLogistInternal,
    ProfileCallCenterManagerInternal,
    ProfileGeneralCallCenterManagerInternal,
    ProfileSupportInternal,
]

profile_to_schemas_create = {
    enums.ProfileType.BRANCH_MANAGER: ProfileBranchManagerCreate,
    enums.ProfileType.COURIER: ProfileCourierCreate,
    enums.ProfileType.DISPATCHER: ProfileDispatcherCreate,
    enums.ProfileType.MANAGER: ProfileManagerCreate,
    enums.ProfileType.BANK_MANAGER: ProfileBankManagerCreate,
    enums.ProfileType.OWNER: ProfileOwnerCreate,
    enums.ProfileType.PARTNER_BRANCH_MANAGER: ProfilePartnerBranchManagerCreate,
    enums.ProfileType.SERVICE_MANAGER: ProfileServiceManagerCreate,
    enums.ProfileType.SORTER: ProfileSorterCreate,
    enums.ProfileType.SUPERVISOR: ProfileSupervisorCreate,
    enums.ProfileType.LOGIST: ProfileLogistCreate,
    enums.ProfileType.CALL_CENTER_MANAGER: ProfileCallCenterManagerCreate,
    enums.ProfileType.GENERAL_CALL_CENTER_MANAGER: ProfileGeneralCallCenterManagerCreate,
    enums.ProfileType.SUPPORT: ProfileSupportCreate,
}

profile_to_schemas_update = {
    enums.ProfileType.BRANCH_MANAGER: ProfileBranchManagerUpdate,
    enums.ProfileType.COURIER: ProfileCourierUpdate,
    enums.ProfileType.DISPATCHER: ProfileDispatcherUpdate,
    enums.ProfileType.MANAGER: ProfileManagerUpdate,
    enums.ProfileType.BANK_MANAGER: ProfileBankManagerUpdate,
    enums.ProfileType.OWNER: ProfileOwnerUpdate,
    enums.ProfileType.PARTNER_BRANCH_MANAGER: ProfilePartnerBranchManagerUpdate,
    enums.ProfileType.SERVICE_MANAGER: ProfileServiceManagerUpdate,
    enums.ProfileType.SORTER: ProfileSorterUpdate,
    enums.ProfileType.SUPERVISOR: ProfileSupervisorUpdate,
    enums.ProfileType.LOGIST: ProfileLogistUpdate,
    enums.ProfileType.CALL_CENTER_MANAGER: ProfileCallCenterManagerUpdate,
    enums.ProfileType.GENERAL_CALL_CENTER_MANAGER: ProfileGeneralCallCenterManagerUpdate,
    enums.ProfileType.SUPPORT: ProfileSupportUpdate,
}


# This schema has the higher order for creation through API
# and not related to any intermediate pydantic-inherited model
class Profile(pydantic.BaseModel):
    profile_type: enums.ProfileType


class ProfileCreate(Profile):
    user: UserCreate
    profile_content: OneOfProfilesCreate

    @pydantic.root_validator()
    def validate_profile_content(cls, values):  # noqa
        if 'profile_content' not in values:
            return values
        if isinstance(values['profile_content'], dict):
            inner_schema = profile_to_schemas_create[values['profile_type']]
            inner_schema(**values['profile_content'])
        return values


class ProfileUpdate(Profile):
    profile_content: OneOfProfilesUpdate

    @pydantic.root_validator(pre=True)
    def validate_profile_content(cls, values):  # noqa
        if 'profile_content' not in values:
            return values
        if isinstance(values['profile_content'], dict):
            inner_schema = profile_to_schemas_update[values['profile_type']]
            inner_schema(**values['profile_content'])
        return values

    class Config:
        smart_union = True


class ProfileUpdatePatch(Profile):
    profile_content: OneOfProfilesPartialUpdate

    @pydantic.root_validator(pre=True)
    def validate_profile_content(cls, values):  # noqa
        if 'profile_content' not in values:
            return values
        if isinstance(values['profile_content'], dict):
            inner_schema = schema_base.partial(
                profile_to_schemas_update[values['profile_type']],
            )
            inner_schema(**values['profile_content'])
        return values


class ProfileStatusUpdate(pydantic.BaseModel):
    status: typing.Optional[enums.InviteStatus]


class ProfileGet(Profile):
    id: pydantic.StrictInt
    user_id: pydantic.StrictInt
    profile_content: dict

    class Config:
        schema_extra = {
            'example': [
                {
                    'user': {
                        'phone_number': '+77018887879',
                        'iin': '020917500091',
                    },
                    'profile_type': enums.ProfileType.COURIER,
                    'profile_content': {
                        'city_id': 1,
                        'category': 'A',
                        'at_work': True,
                        'start_work_hour': '10:00',
                        'end_work_hour': '20:00',
                        'experience_years': 10,
                        'experience_months': 3,
                        'schedule': [
                            'monday',
                            'tuesday',
                            'wednesday',
                            'thursday',
                            'friday',
                            'saturday',
                            'sunday',
                        ],
                        'is_identified': False,
                        'is_biometry_verificated': False,
                    },
                },
                {
                    'id': 1,
                    'user': {
                        'phone_number': '+77018887879',
                        'iin': '020917500091',
                    },
                    'profile_type': enums.ProfileType.SERVICE_MANAGER,
                    'profile_content': {},
                },
                {
                    'id': 1,
                    'user': {
                        'phone_number': '+77018887879',
                        'iin': '020917500091',
                    },
                    'profile_type': enums.ProfileType.MANAGER,
                    'profile_content': {},
                },
                {
                    'id': 1,
                    'user': {
                        'phone_number': '+77018887879',
                        'iin': '020917500091',
                    },
                    'profile_type': enums.ProfileType.OWNER,
                    'profile_content': {},
                },
            ],
        }


# We should not pass fields that must be validated
class ProfileDelete(Profile):
    pass


class ProfileInternal(Profile):
    user_id: pydantic.StrictInt
    profile_content: OneOfProfilesInternal

    @pydantic.root_validator(skip_on_failure=True)
    def validate_profile_content(cls, values):  # noqa
        if 'profile_content' not in values:
            return values
        if isinstance(values['profile_content'], dict):
            inner_schema = profile_to_schemas_create[values['profile_type']]
            inner_schema(**values['profile_content'])
        return values


class CourierDevicesSave(pydantic.BaseModel):
    courier_id: pydantic.StrictInt
    device_id: pydantic.StrictStr


class UserBasicFields(pydantic.BaseModel):
    id: int
    first_name: str | None
    middle_name: str | None
    last_name: str | None
    is_active: bool | None

    class Config:
        orm_mode = True


class CourierList(pydantic.BaseModel):
    id: int
    user: UserBasicFields

    class Config:
        orm_mode = True


class CourierFilter(pydantic.BaseModel):
    city_id: int | None
    status: enums.InviteStatus | None

    class Config:
        use_enum_values = True
