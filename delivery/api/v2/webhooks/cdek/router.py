import fastapi
from api.v2.webhooks.cdek.order_status import router as order_status_router

router = fastapi.APIRouter(prefix='/cdek')

router.include_router(order_status_router)
