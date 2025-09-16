#TODO: it needs to be refactor

import json
import typing
from typing import Dict
from typing import List

from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from .. import schemas
from .. import enums
from ..services import ws_monitoring


class ConnectionManager:
    def __init__(self):
        self.active_couriers: dict[int, WebSocket] = {}
        self.active_monitors: Dict[int, List[WebSocket]] = {}
        self.active_managers: dict[int, List[WebSocket]] = {}
        self.active_clients: dict[str, List[WebSocket]] = {}

    async def connect_monitor(self, websocket: WebSocket, courier_service_id: int):
        if self.active_monitors.get(courier_service_id) is None:
            self.active_monitors[courier_service_id] = []
        self.active_monitors[courier_service_id].append(websocket)

    async def connect_client(self, order_id, websocket: WebSocket):
        if self.active_clients.get(order_id) is None:
            self.active_clients[order_id] = []
        self.active_clients[order_id].append(websocket)

    async def connect_courier(self, courier_id, websocket: WebSocket):
        self.active_couriers[courier_id] = websocket

    async def connect_manager(self, partner_id, websocket: WebSocket):
        if self.active_managers.get(partner_id) is None:
            self.active_managers[partner_id] = []
        self.active_managers[partner_id].append(websocket)

    def disconnect_monitor(self, websocket: WebSocket, city_id: int):
        if websocket in self.active_monitors[city_id]:
            self.active_monitors[city_id].remove(websocket)

    def disconnect_courier(self, websocket: WebSocket):
        for courier_id in list(self.active_couriers.keys()):
            if self.active_couriers[courier_id] == websocket:
                del self.active_couriers[courier_id]

    def disconnect_manager(self, websocket: WebSocket):
        for partner_id in list(self.active_managers.keys()):
            if websocket in self.active_managers[partner_id]:
                self.active_managers[partner_id].remove(websocket)

    def disconnect_client(self, websocket: WebSocket, phone_number: str):
        if websocket in self.active_clients[phone_number]:
            self.active_clients[phone_number].remove(websocket)

    async def send_all_locations(self, websocket: WebSocket, courier_service_id: int):
        couriers = await ws_monitoring.service.get_locations(courier_service_id)
        message = {
            'type': enums.MessageType.LOCATION.value,
            'data': couriers
        }
        await websocket.send_json(message)

    async def send_location(self, websocket: WebSocket, courier_id: int, courier_service_id: int):
        location = await ws_monitoring.service.get_location(courier_service_id, courier_id)
        try:
            message = {
                'type': enums.MessageType.LOCATION.value,
                'data': json.loads(location) if location else 'Not data'
            }
            await websocket.send_json(message)
        except IndexError:
            await websocket.send_json({'msg': 'Courier location not found!'})

    async def send_last_location(
            self, courier_service_id: int, courier_id: int,
            location, order_ids: typing.List[int]
    ):
        message = {
            'type': enums.MessageType.LOCATION.value,
            'data': {
                'courier_id': courier_id,
                'location': location,
                'is_active': True
            }
        }
        for active_monitor in self.active_monitors.get(courier_service_id, []):
            await active_monitor.send_json(message)

        for order_id in order_ids:
            if str(order_id) in list(self.active_clients.keys()):
                for socket in self.active_clients.get(str(order_id)):
                    await socket.send_json(message)

    async def send_message_for_managers(self, partner_id: int, message: dict):
        partners = self.active_managers.get(partner_id)
        if partners:
            for websocket in partners:
                try:
                    await websocket.send_json(
                        message
                    )
                except (WebSocketDisconnect, RuntimeError):
                    self.active_managers[partner_id].remove(websocket)

    async def send_new_order(self, courier_id, order: schemas.OrderGet):
        order = order.json(encoder=str)
        order = json.loads(order)
        data = json.dumps({'new_order': {'order': order}}, default=str)
        message = {
            'type': enums.MessageType.NEW_ORDER.value,
            'data': data
        }
        if courier_id in self.active_couriers:
            await self.active_couriers[courier_id].send_json(message)

    async def send_order_status_update(self, order_id, order_status):
        message = {
            'type': enums.MessageType.ORDER_STATUS_UPDATE.value,
            'data': json.dumps(order_status, default=str)
        }

        if clients := self.active_clients.get(str(order_id)):
            for websocket in clients:
                try:
                    await websocket.send_json(message)
                except WebSocketDisconnect:
                    self.active_clients[order_id].remove(websocket)


websocket_manager = ConnectionManager()
