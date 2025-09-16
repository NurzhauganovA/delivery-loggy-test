from typing import List

from fastapi.encoders import jsonable_encoder

from api.controllers.websocket_managers import websocket_manager

from ... import models
from ... import services
from ... import schemas

from .schemas import (
    GeolocationPut
)

from ...common.action_base import BaseAction


class GeolocationActions(BaseAction):
    __MESSAGE_TYPE = 'location'

    def __init__(self):
        self.__active_monitors = websocket_manager.active_monitors
        self.__active_clients = websocket_manager.active_clients

    async def geolocation_put(
        self, geolocation: GeolocationPut
    ):
        location_data = schemas.MonitoringLocation(
            courier_service_id=geolocation.courier_partner_id,
            location=schemas.Coordinates(
                latitude=geolocation.latitude,
                longitude=geolocation.longitude,
            )
        ).dict()
        await services.ws_monitoring.service.update_courier_location(
            courier_service_id=geolocation.courier_partner_id,
            courier_id=geolocation.courier_id,
            location={
                'latitude': geolocation.latitude,
                'longitude': geolocation.longitude,
            },
        )
        message = jsonable_encoder({
            'type': self.__MESSAGE_TYPE,
            'data': {
                'courier_id': geolocation.courier_id,
                'location': location_data,
                'is_active': True
            }
        })

        await self.__send_location_to_managers(
            courier_partner_id=geolocation.courier_partner_id, message=message
        )

        if order_ids := await (
            models.order_get_couriers_current_executable_orders(geolocation.courier_id)
        ):
            await self.__send_location_to_clients(
                order_ids=order_ids, message=message
            )

    async def __send_location_to_managers(self, courier_partner_id: int, message: dict) -> None:
        for active_monitor in self.__active_monitors.get(courier_partner_id, []):
            await active_monitor.send_json(message)

    async def __send_location_to_clients(
        self, order_ids: List[int], message: dict) -> None:
        for order_id in order_ids:
            if str(order_id) in list(self.__active_clients.keys()):
                for socket in self.__active_clients.get(str(order_id)):
                    await socket.send_json(message)