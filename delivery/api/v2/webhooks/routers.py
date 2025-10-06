import fastapi
from api.v2.webhooks.cdek.router import router as cdek_router

router = fastapi.APIRouter(prefix='/webhooks')

router.include_router(cdek_router)
