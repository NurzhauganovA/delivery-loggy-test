import typing
import uuid

import fastapi

from ... import auth
from ... import controllers
from ... import schemas
from ... import services
from ... import enums

router = fastapi.APIRouter()


@router.get(
    '/external_service',
    summary='Get external service history object',
    response_model=typing.List[schemas.ExternalServiceHistoryGet],
    response_description='External service history',
)
async def external_service_history_get(
    id_: uuid.UUID,
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
) -> dict:
    """Get a list of orders."""
    return await controllers.external_service_history_get(id_=id_)


@router.get(
    '/external_service/list',
    summary='Get external service history',
    response_model=typing.List[schemas.ExternalServiceHistoryGet],
    response_description='External service history',
)
async def external_service_history_get_list(
    filtration: schemas.ExternalServiceHistoryGetList = fastapi.Depends(schemas.ExternalServiceHistoryGetList),
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
) -> list:
    """Get a list of orders."""
    return await controllers.external_service_history_get_list(**filtration.dict(exclude_unset=True, exclude_none=True))


@router.post(
    '/external_service/configure_dataloader',
    summary='Configure dataloader',
    response_description='Success',
)
async def external_service_history_configure_dataloader(
    current_user: schemas.UserCurrent = fastapi.Security(
        auth.get_current_user,
    ),
) -> fastapi.Response:
    """Need to provide current_user to dataloader"""
    services.dataloader.service.current_user_id = current_user.id
    return fastapi.Response()
