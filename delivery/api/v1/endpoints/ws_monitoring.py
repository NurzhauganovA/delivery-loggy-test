from fastapi import APIRouter
from fastapi import WebSocket

from ... import controllers

router = APIRouter()


@router.websocket('/monitoring/courier')
async def courier(websocket: WebSocket):
    await controllers.courier(websocket)


@router.websocket('/monitoring/manager')
async def manager(websocket: WebSocket):
    await controllers.manager(websocket)


@router.websocket('/monitoring/client')
async def client(websocket: WebSocket):
    await controllers.client(websocket)


@router.websocket('/monitoring/monitor/{courier_service_id}')
async def monitoring(websocket: WebSocket, courier_service_id: int):
    await controllers.monitor(websocket, courier_service_id)
