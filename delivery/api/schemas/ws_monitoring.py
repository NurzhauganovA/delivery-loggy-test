import pydantic

from .place import Coordinates


class MonitoringLocation(pydantic.BaseModel):
    courier_service_id: int
    location: Coordinates


class CurrentLocationRequest(pydantic.BaseModel):
    courier_service_id: int
    courier_id: int
