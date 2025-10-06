from pydantic import BaseModel


class Attributes(BaseModel):
    code: str


class OrderStatusRequest(BaseModel):
    uuid: str
    attributes: Attributes
