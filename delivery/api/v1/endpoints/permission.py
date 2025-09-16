from typing import List

from fastapi import APIRouter
from fastapi import Security
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth
from ... import controllers
from ... import schemas


router = APIRouter()


@router.get(
    '/permissions',
    summary='List permissions',
    response_model=List[schemas.PermissionList],
    response_description='Permission',
)
async def permission_list(
    _: schemas.UserCurrent = Security(
        auth.get_current_user,
        scopes=['pm:l'],
    ),
):
    """List permissions"""
    result = await controllers.permission_list()
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/permissions/{permission_slug}',
    summary='List permissions',
    response_model=schemas.PermissionGet,
    response_description='Permission',
)
async def permission_get(
    permission_slug: str,
    _: schemas.UserCurrent = Security(
        auth.get_current_user,
        scopes=['pm:g'],
    ),
):
    """Get permission with given slug"""
    result = await controllers.permission_get(permission_slug)
    return JSONResponse(jsonable_encoder(result))
