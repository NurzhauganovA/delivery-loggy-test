from pydantic import BaseModel

from api.enums import ProductType


class Product(BaseModel):
    id: int
    order_id: int
    type: ProductType
    attributes: dict
