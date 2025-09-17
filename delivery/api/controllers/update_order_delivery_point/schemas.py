import pydantic


class DeliveryPoint(pydantic.BaseModel):
    latitude: float
    longitude: float
    address: str


class ValidDeliveryPoint(pydantic.BaseModel):
    delivery_point: DeliveryPoint
    comment: str
