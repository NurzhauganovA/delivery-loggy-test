import fastapi

from api.v2.endpoints import comments
from ..modules.shipment_point import v2 as shipment_point
from .endpoints import (
    order,
    user,
    courier,
)
from api.v2 import crm
from api.v2 import mobile


api_router = fastapi.APIRouter(prefix='/v2')
api_router.include_router(shipment_point.router, tags=['shipment_point'])
api_router.include_router(order.router, tags=['order'])
api_router.include_router(user.router, tags=['user'])
api_router.include_router(comments.router, tags=['comments'])
api_router.include_router(crm.router, tags=['crm'])
api_router.include_router(mobile.router, tags=['mobile'])
api_router.include_router(courier.router, tags=['courier'])
