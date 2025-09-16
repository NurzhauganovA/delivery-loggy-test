import fastapi
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse
from tortoise.expressions import Q

from api import schemas, exceptions
from api.auth import get_current_user
from api.controllers.comments.attach_image_to_comment.controller import attach_image_to_comment as attach_image_to_comment_controller
from api.controllers.comments.attach_image_to_comment.exceptions import CommentAttachImageException
from api.dependencies import OrderDefaultFilterV2
from api.dependencies.image import get_comment_image_validator
from api.schemas.comments.attach_image_to_comment.response import CommentAttachImageResponse
from api.utils.image.exceptions import ImageValidationError
from api.utils.image.image_validator import ImageValidator

router = fastapi.APIRouter()


@router.post(
    '/order/{order_id}/comments/{comment_id}/images',
    response_model=CommentAttachImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def attach_image_to_comment(
    order_id: int,
    comment_id: int,
    image: fastapi.UploadFile = fastapi.File(...),
    image_validator: ImageValidator = fastapi.Depends(get_comment_image_validator),
    current_user: schemas.UserCurrent = fastapi.Security(
        get_current_user,
        scopes=['oci:c'],
    ),
    order_filters: list[Q] = fastapi.Depends(OrderDefaultFilterV2()),
):
    try:
        await image_validator.validate(image)
    except ImageValidationError as e:
        raise exceptions.HTTPBadRequestException(e)

    serialized_photo = await image_validator.serialize_image(image)

    try:
        attached_image_id = await attach_image_to_comment_controller(
            order_id=order_id,
            order_filters=order_filters,
            comment_id=comment_id,
            current_user=current_user,
            image=serialized_photo,
        )
    except CommentAttachImageException as e:
        raise exceptions.HTTPBadRequestException(e)

    response_data = CommentAttachImageResponse(id=attached_image_id)
    return JSONResponse(jsonable_encoder(response_data), status_code=201)
