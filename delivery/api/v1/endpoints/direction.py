import os
import typing

import fastapi

from ... import auth
from ... import controllers
from ... import schemas
from ... import utils

router = fastapi.APIRouter()


@router.get(
    '/direction/mobile',
    summary='Get osm direction',
    response_model=typing.List[schemas.DirectionGet],
    response_description='Direction route',
)
async def order_get_direction_mobile(
        current_user: schemas.UserCurrent = fastapi.Security(
            auth.get_current_user,
            # scopes=['o:l']
        ),
) -> list:
    """Get a list of orders."""
    return await controllers.direction_get(
        current_user=current_user,
    )
