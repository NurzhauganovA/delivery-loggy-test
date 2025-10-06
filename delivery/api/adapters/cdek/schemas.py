from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
)


class CreateOrder(BaseModel):
    shipment_point: str
    recipient_name: str
    recipient_phone: str
    latitude: Decimal = Field(gt=0)
    longitude: Decimal = Field(gt=0)
    address: str
    package_number: str
