from decimal import Decimal

from httpx import HTTPError
from pydantic import ValidationError

from api.clients.cdek import CDEKClient
from api.clients.cdek.schemas.create_order.request import CreateOrderRequest
from .exceptions import (
    CDEKGetLocationError,
    CDEKValidationError,
    CDEKCreateOrderError,
)
from .schemas import CreateOrder


class CDEKAdapter:
    def __init__(self, client: CDEKClient):
        self.__client = client

    async def order_create(
            self,
            shipment_point: str,
            recipient_name: str,
            recipient_phone: str,
            latitude: Decimal,
            longitude: Decimal,
            address: str,
            package_number: str,
    ) -> str:
        """
            Создание заявки в CDEK

            Args:
                shipment_point: номер склада CDEK в конкретном городе
                recipient_name: ФИО получателя
                recipient_phone: номер телефона получателя
                latitude: широта
                longitude: долгота
                address: адрес получателя
                package_number: номер упаковки (ID заявки в LOGGY)

            Returns:
                Трек номер заявки CDEK
        """

        # Валидация переданных аргументов
        try:
            CreateOrder(
                shipment_point=shipment_point,
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                latitude=latitude,
                longitude=longitude,
                address=address,
                package_number=package_number,
            )
        except ValidationError as e:
            raise CDEKValidationError(e) from e

        # Сперва нужно получить локацию от CDEK по координатам
        try:
            response = await self.__client.get_location(
                latitude=float(latitude),
                longitude=float(longitude),
            )
        except HTTPError as e:
            raise CDEKGetLocationError(e) from e

        location_data = response.json()

        # Затем с полученными данными по локации создать заявку в CDEK
        request = CreateOrderRequest.create(
            shipment_point=shipment_point,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            location_code=location_data['code'],
            city=location_data['city'],
            fias_guid=location_data['fias_guid'],
            latitude=float(latitude),
            longitude=float(longitude),
            address=address,
            package_number=package_number,
        )
        try:
            response = await self.__client.create_order(
                request=request
            )
        except HTTPError as e:
            raise CDEKCreateOrderError(e) from e

        order_data = response.json()

        # Достанем трек номер CDEK
        track_number = order_data['entity']['uuid']

        return track_number
