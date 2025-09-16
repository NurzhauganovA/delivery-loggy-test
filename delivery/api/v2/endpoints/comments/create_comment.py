import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from tortoise.expressions import Q

from api import dependencies
from api import exceptions
from api import schemas
from api.auth import get_current_user
from api.controllers.comments.create_comment.exceptions import CommentCreateException
from api.schemas.comments.create_comment.request import CreateCommentRequest
from api.schemas.comments.create_comment.response import CreateCommentResponse
from api.controllers.comments.create_comment.controller import create_comment as create_comment_controller

router = fastapi.APIRouter()


@router.post(
    '/order/{order_id}/comments',
    response_model=CreateCommentResponse,
    status_code=201,
)
async def create_comment(
    order_id: int,
    comment: CreateCommentRequest,
    user: schemas.UserCurrent = fastapi.Security(get_current_user, scopes=['oc:c']),
    order_filters: list[Q] = fastapi.Depends(dependencies.OrderDefaultFilterV2()),
):
    try:
        comment_id = await create_comment_controller(
            comment_text=comment.text,
            user=user,
            order_id=order_id,
            order_filters=order_filters,
        )
    except CommentCreateException as e:
        raise exceptions.HTTPBadRequestException(e)

    response_data = CreateCommentResponse(id=comment_id)
    return JSONResponse(jsonable_encoder(response_data), status_code=201)
