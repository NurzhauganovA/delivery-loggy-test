from decimal import Decimal

from api.common.schema_base import BaseInSchema


class Coordinates(BaseInSchema):
    latitude: Decimal | None = None
    longitude: Decimal | None = None

    def to_tuple(self):
        return self.latitude, self.longitude
