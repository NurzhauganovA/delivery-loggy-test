import pydantic


class DeliveryPoint(pydantic.BaseModel):
    latitude: float
    longitude: float
    address: str


class ValidDeliveryPoint(pydantic.BaseModel):
    city_id: pydantic.conint(ge=1) | None
    delivery_point: DeliveryPoint
    comment: str
