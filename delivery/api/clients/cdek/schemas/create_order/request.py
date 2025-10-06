from typing import List, Literal

from pydantic import BaseModel, Field


class Phone(BaseModel):
    number: str


class Sender(BaseModel):
    company: Literal["Freedom Bank"] = Field(default="Freedom Bank")
    name: Literal["Freedom Bank"] = Field(default="Freedom Bank")
    contragent_type: Literal["LEGAL_ENTITY"] = Field(default="LEGAL_ENTITY")
    phones: List[Phone] = Field(default=[Phone(number="87071234567")], description="Номер колл-центра")


class Recipient(BaseModel):
    name: str
    phones: List[Phone]


class ToLocation(BaseModel):
    code: int
    city: str
    fias_guid: str
    longitude: float
    latitude: float
    address: str


class Package(BaseModel):
    number: str = Field(description="Номер заказа, order_id")
    weight: float = Field(default=0.1)
    length: int = Field(default=1)
    width: int = Field(default=1)
    height: int = Field(default=1)
    comment: Literal["Карта"] = Field(default="Карта")


class CreateOrderRequest(BaseModel):
    type: Literal[2] = Field(default=2)
    tariff_code: Literal[482] = Field(default=482)
    shipment_point: str
    sender: Sender = Field(default=Sender())
    recipient: Recipient
    to_location: ToLocation
    packages: List[Package]
    is_client_return: bool = Field(default=False)
    has_reverse_order: bool = Field(default=False)
    developer_key: Literal["freedom-loggy"] = Field(default="freedom-loggy")

    @classmethod
    def create(
            cls,
            shipment_point: str,
            recipient_name: str,
            recipient_phone: str,
            location_code: int,
            city: str,
            fias_guid: str,
            latitude: float,
            longitude: float,
            address: str,
            package_number: str,
    ) -> 'CreateOrderRequest':
        """
            Метод конструктор, принимающий аргументы плоско и скрывающий внутренние детали реализации схемы
        """
        return CreateOrderRequest(
            shipment_point=shipment_point,
            recipient=Recipient(
                name=recipient_name,
                phones=[
                    Phone(number=recipient_phone)
                ]
            ),
            to_location=ToLocation(
                code=location_code,
                city=city,
                fias_guid=fias_guid,
                latitude=latitude,
                longitude=longitude,
                address=address,
            ),
            packages=[
                Package(
                    number=package_number,
                )
            ]
        )
