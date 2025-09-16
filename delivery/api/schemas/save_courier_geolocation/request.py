import decimal

from pydantic import BaseModel


class SaveCourierGeolocation(BaseModel):
    latitude: decimal.Decimal
    longitude: decimal.Decimal
    order_id: int
