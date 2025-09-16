import typing

from fastapi import Query
import pydantic

from .place import Coordinates


class AreaFilter(pydantic.BaseModel):
    city_id: int | None
    archived: bool = Query(False)


class Place(pydantic.BaseModel):
    id: int
    address: str
    latitude: float
    longitude: float

    class Config:
        orm_mode = True


class ShipmentPoint(pydantic.BaseModel):
    id: int
    place: Place

    class Config:
        orm_mode = True


class AreaBase(pydantic.BaseModel):
    slug: pydantic.constr(strict=True, max_length=255)
    city_id: pydantic.conint(gt=0, le=2_147_483_647)
    scope: typing.List[Coordinates]
    fill_color: pydantic.constr(max_length=15)
    fill_opacity: pydantic.confloat(ge=0.0, le=1.0)
    stroke_color: pydantic.constr(max_length=15)
    stroke_opacity: pydantic.confloat(ge=0.0, le=1.0)


class AreaCreate(AreaBase):
    partner_id: int


class AreaGet(AreaBase):
    id: pydantic.StrictInt
    partner_id: int
    shipment_points: typing.List[ShipmentPoint] = []
    courier_number: typing.Optional[int] = 0

    class Config:
        orm_mode = True


class AreaUpdate(AreaBase):
    pass


class AreaInternal(AreaBase):
    pass
