import fastapi
from api.v2.crm.order import router as order_router

router = fastapi.APIRouter(prefix='/crm')

router.include_router(order_router)
