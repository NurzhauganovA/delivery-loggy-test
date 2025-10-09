import fastapi
from api.v2.crm.order import router as order_router
from api.v2.crm.cdek_auth import router as cdek_auth_router

router = fastapi.APIRouter(prefix='/crm')

router.include_router(order_router)
router.include_router(cdek_auth_router)
