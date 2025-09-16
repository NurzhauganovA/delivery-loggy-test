from typing import List

import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ... import auth
from ... import controllers
from ... import schemas


router = fastapi.APIRouter()


@router.post(
    '/group',
    summary='Create group',
    response_model=schemas.Group,
    response_description='Group',
)
async def group_create(
    group: schemas.GroupCreate,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['g:c'],
    ),
):
    """Create group with given data"""
    result = await controllers.group_create(group)
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/group',
    summary='List group',
    response_model=List[schemas.GroupList],
    response_description='Group list',
)
async def group_list(
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['g:l'],
    ),
):
    """List group"""
    result = await controllers.group_list()
    return JSONResponse(jsonable_encoder(result))


@router.get(
    '/group/{group_slug}',
    summary='Detail get group with given slug',
    response_model=schemas.GroupGet,
)
async def group_get(
    group_slug: str,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['g:g'],
    ),
):
    """Get group with given slug"""
    result = await controllers.group_get(group_slug)
    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/group/{group_slug}/add_user',
    summary='Add user to group',
    response_model=schemas.GroupGet,
    response_description='Group update',
)
async def group_user_add(
    group_slug: str,
    user_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['g:ua'],
    ),
):
    result = await controllers.group_user_add(group_slug, user_id)
    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/group/{group_slug}/remove_user',
    summary='Remove user from group',
    response_model=schemas.GroupGet,
    response_description='Group update',
)
async def group_user_remove(
    group_slug: str,
    user_id: int,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['g:ur'],
    ),
):
    result = await controllers.group_user_remove(group_slug, user_id)
    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/group/{group_slug}/add_permission',
    summary='Add permission to group',
    response_model=schemas.GroupGet,
    response_description='Group update',
)
async def group_permission_add(
    group_slug: str,
    permission_slug: str,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pm:ga'],
    ),
):
    result = await controllers.group_permission_add(group_slug, permission_slug)
    return JSONResponse(jsonable_encoder(result))


@router.put(
    '/group/{group_slug}/remove_permission',
    summary='Remove permission from group',
    response_model=schemas.GroupGet,
    response_description='Group update',
)
async def group_permission_remove(
    group_slug: str,
    permission_slug: str,
    _: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
        scopes=['pm:gr'],
    ),
):
    result = await controllers.group_permission_remove(group_slug, permission_slug)
    return JSONResponse(jsonable_encoder(result))
