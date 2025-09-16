#TODO: it needs to be refactor

import json

from pydantic import ValidationError
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from .. import auth
from .. import exceptions
from .. import schemas
from .. import models
from .. import enums
from ..services import ws_monitoring
from .websocket_managers import websocket_manager


async def ws_authenticate(websocket) -> schemas.UserCurrent:
    message = {
        'type': enums.MessageType.REQUEST.value,
        'msg': 'Please send authorization token'
    }
    await websocket.send_json(message)
    while True:
        raw_token = await websocket.receive_text()
        try:
            current_user = await auth.get_current_user(token=raw_token)
            if not current_user.profile:
                raise exceptions.HTTPUnauthenticatedException()
            return current_user
        except exceptions.HTTPUnauthenticatedException:
            await websocket.send_json(
                {
                    'type': enums.MessageType.ERROR.value,
                    'msg': 'Invalid token, please send authorization token again',
                }
            )


async def ws_authenticate_client(websocket) -> schemas.UserCurrent:
    message = {
        'type': enums.MessageType.REQUEST.value,
        'msg': 'Please send your order id'
    }
    await websocket.send_json(message)
    while True:
        raw_token = await websocket.receive_text()
        try:
            await models.order_ensure_exists(raw_token)
            return raw_token
        except models.OrderNotFound as e:
            await websocket.send_json({
                'msg': str(e),
            })


async def manager(websocket: WebSocket):
    message_success = {
        'type': enums.MessageType.SUCCESS.value,
        'msg': 'You are connected!'
    }
    await websocket.accept()
    try:
        current_user = await ws_authenticate(websocket)
        partners = current_user.partners
        if partners:
            for partner in partners:
                await websocket_manager.connect_manager(
                    partner,
                    websocket)
        else:
            await websocket_manager.connect_manager(
                current_user.profile.get('profile_content').get('partner_id'),
                websocket)
        try:
            await websocket.send_json(message_success)
            await websocket.receive_json()
        except json.JSONDecodeError:
            pass
        except ValidationError as e:
            await websocket.send_json(e.errors())
    except WebSocketDisconnect:
        websocket_manager.disconnect_manager(websocket)


async def client(websocket: WebSocket):
    success_message = {
        'type': enums.MessageType.SUCCESS.value,
        'msg': 'You are connected!'
    }
    request_message = {
        'type': enums.MessageType.REQUEST.value,
        'msg': 'Insert id of your courier!'
    }
    error_message = {
        'type': enums.MessageType.ERROR.value,
        'msg': 'Message must be a json!'
    }
    await websocket.accept()
    order_id = await ws_authenticate_client(websocket)
    try:

        await websocket_manager.connect_client(
            websocket=websocket,
            order_id=order_id
        )
        await websocket.send_json(success_message)
        await websocket.send_json(request_message)
        while True:
            data = await websocket.receive_json()
            try:
                validated_data = schemas.CurrentLocationRequest(**data).dict()
            except ValidationError as e:
                await websocket.send_json({
                    'type': enums.MessageType.ERROR.value,
                    'msg': e.errors()
                })
                continue
            except TypeError:
                await websocket.send_json(error_message)
                continue

            await websocket_manager.send_location(websocket=websocket, **validated_data)
    except WebSocketDisconnect:
        websocket_manager.disconnect_client(websocket, order_id)


async def courier(websocket: WebSocket):
    request_message = {
        'type': enums.MessageType.REQUEST.value,
        'msg': 'Now, you can send location!'
    }

    error_message = {
        'type': enums.MessageType.ERROR.value,
        'msg': 'Courier have not orders in executable!'
    }

    success_message = {
        'type': enums.MessageType.SUCCESS.value,
        'msg': 'Your current location accepted!'
    }
    await websocket.accept()
    try:
        current_user = await ws_authenticate(websocket)
        profile = current_user.profile.get('profile_content', None)
        await websocket_manager.connect_courier(current_user.id, websocket)
        await websocket.send_json(request_message)
        while True:
            try:
                data = await websocket.receive_json()
                data['courier_service_id'] = profile.get('partner_id')

                validated_data = schemas.MonitoringLocation(**data).dict()
                courier_id = current_user.profile.get('id')
                order_ids = await (
                    models.order_get_couriers_current_executable_orders(courier_id)
                )

                if not order_ids:
                    await websocket.send_json(
                        error_message,
                    )

                await ws_monitoring.service.update_courier_location(
                    courier_id=courier_id,
                    **validated_data,
                )

                await websocket_manager.send_last_location(
                    courier_id=current_user.profile.get('id'),
                    order_ids=order_ids,
                    location=validated_data.get('location'),
                    courier_service_id=validated_data.get('courier_service_id')
                )

                await websocket.send_json(
                    success_message,
                )
            except json.JSONDecodeError:
                pass
            except ValidationError as e:
                await websocket.send_json({
                    'type': enums.MessageType.ERROR.value,
                    'msg': e.errors()
                })
    except WebSocketDisconnect:
        websocket_manager.disconnect_courier(websocket)


async def monitor(websocket: WebSocket, courier_service_id: int):
    await websocket.accept()
    await websocket_manager.connect_monitor(websocket, courier_service_id)
    try:
        while True:
            command = await websocket.receive_text()
            if command == 'data':
                await websocket_manager.send_all_locations(websocket, courier_service_id)
            else:
                await websocket.send_json(
                    {
                        'type': enums.MessageType.ERROR.value,
                        'msg':  f'There is no such command: `{command}`',
                    }
                )
    except WebSocketDisconnect:
        websocket_manager.disconnect_monitor(websocket, courier_service_id)
