from asyncpg import Range as RangeBase
from pydantic import BaseModel


class DateRange(BaseModel):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            #  assumes v given as: "[YYYY-MM-DD, YYYY-MM-DD)", [],() are bounds
            lower = v.split(", ")[0][1:].strip().strip()
            upper = v.split(", ")[1][:-1].strip().strip()
            return RangeBase(lower, upper, lower_inc=v[:1] == '[', upper_inc=v[-1:] == ']')
        elif isinstance(v, RangeBase):
            return v
        raise TypeError("Type must be string or Range")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='[Date, Date]', example='[2022,01,01, 2022,02,02)')

