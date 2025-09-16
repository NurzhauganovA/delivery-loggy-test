import fastapi
from api.v2.mobile.history import router as history_router

router = fastapi.APIRouter(prefix='/mobile')

router.include_router(history_router)
