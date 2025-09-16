import pydantic

from . import place
from api.common import validators


class MonitoringCourierBase(place.Coordinates):
    id: pydantic.StrictInt
    city_id: pydantic.StrictInt
    first_name: str
    last_name: str
    ts: pydantic.StrictInt

    _v_lt = validators.reuse('latitude')(validators.validate_latitude_to_float)
    _v_ln = validators.reuse('longitude')(validators.validate_longitude_to_float)


class MonitoringCourier(MonitoringCourierBase):
    pass


class MonitoringCourierAdd(MonitoringCourier):
    pass


class MonitoringCourierGet(MonitoringCourier):
    pass
