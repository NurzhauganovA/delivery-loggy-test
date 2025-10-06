from decimal import Decimal

from api.common.schema_base import BaseInSchema


class CDEKOrder(BaseInSchema):
    latitude: Decimal
    longitude: Decimal
    address: str
    warehouse_id: str
