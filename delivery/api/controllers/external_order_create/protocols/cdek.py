from typing import Protocol


class CreateOrderRequestProtocol(Protocol):
    """Интерфейс схемы запроса на создание заявки в CDEK"""
    shipment_point: str
    recipient_name: str
    recipient_phone: str
    latitude: float
    longitude: float
    address: str
    package_number: str


class CDEKOrderCreationProtocol(Protocol):
    async def order_create(self, request: CreateOrderRequestProtocol):
        """Создание заявки в CDEK"""
