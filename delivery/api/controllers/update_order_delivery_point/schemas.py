import pydantic


class DeliveryPoint(pydantic.BaseModel):
    latitude: float
    longitude: float
    address: str


class Courier(pydantic.BaseModel):
    delivery_point: DeliveryPoint
    comment: str


class Supervisor(pydantic.BaseModel):
    delivery_point: DeliveryPoint
