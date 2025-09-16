import typing
from datetime import datetime, date
from random import uniform
from typing import Optional

import pydantic

from api.enums import ProgressInterval


class StatisticsBaseDetail(pydantic.BaseModel):
    name: Optional[str]
    count: Optional[int]


class CityStatistics(pydantic.BaseModel):
    name: Optional[str]
    statuses: typing.List[StatisticsBaseDetail]


class StatisticsBase(pydantic.BaseModel):
    statuses: typing.List[StatisticsBaseDetail]
    cities: typing.List[CityStatistics]


class StatisticsFilter(pydantic.BaseModel):
    city_id: Optional[int]
    courier_id: Optional[int]
    partner_id: Optional[int]
    from_date: Optional[datetime]
    to_date: Optional[datetime]


class HeatmapResponseItem(pydantic.BaseModel):
    count: int
    latitude: float
    longitude: float

    # noinspection PyMethodParameters
    @pydantic.validator('latitude', 'longitude')
    def randomize_geodata(cls, value):
        return round(uniform(value - 0.005, value + 0.005), 5)


class HeatmapResponse(pydantic.BaseModel):
    max: int
    data: typing.List[HeatmapResponseItem]


class CourierStatFilter(pydantic.BaseModel):
    courier_id: int
    from_date: date | None
    to_date: date | None = datetime.now().date()

    class Config:
        arbitrary_types_allowed = True

    def to_string(self, from_date: date):
        from_date = self.from_date or from_date
        result = (f"AND courier_id = {self.courier_id}"
                  f" AND created_at >= '{from_date.strftime('%Y-%m-%d')}'"
                  f" AND created_at <= '{self.to_date.strftime('%Y-%m-%d')}'")

        return result


class CourierProgressFilter(pydantic.BaseModel):
    courier_id: int
    from_date: date | None
    to_date: date | None = datetime.now().date()
    interval: ProgressInterval

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True

    def to_string(self, from_date):
        from_date = self.from_date or from_date
        result = (f"generate_series('{from_date.strftime('%Y-%m-%d')}'::date,"
                  f" '{self.to_date.strftime('%Y-%m-%d')}'::date,"
                  f" '1 {self.interval}'::interval)")

        return result


class CourierStatGet(pydantic.BaseModel):
    courier_id: int
    avg_reaction_time: int
    avg_completion_time: int
    order_count: int | None

    class Config:
        orm_mode = True


class CourierProgressGet(pydantic.BaseModel):
    avg_reaction_time: int | None
    avg_completion_time: int | None
    order_count: Optional[int]
    date: date | None
