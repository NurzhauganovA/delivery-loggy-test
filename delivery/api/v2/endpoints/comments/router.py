import fastapi

from api.v2.endpoints.comments.attach_image_to_comment import router as attach_image_to_comment_router
from api.v2.endpoints.comments.create_comment import router as create_comment_router

router = fastapi.APIRouter()

router.include_router(create_comment_router)
router.include_router(attach_image_to_comment_router)
