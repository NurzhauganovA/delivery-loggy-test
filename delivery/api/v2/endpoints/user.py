from typing import Annotated

from fastapi import APIRouter, Body
from fastapi import Security
from pydantic import constr
from ... import controllers, auth
from ...schemas import UserCurrent
from ...security import oauth2_scheme

router = APIRouter()


@router.put(
    '/user/set-password',
    status_code=200,
)
async def set_password_v2(
    password: Annotated[constr(min_length=6, max_length=20), Body(embed=True)],
    token: str = Security(oauth2_scheme),
    current_user: UserCurrent = Security(auth.get_current_user),
):
    """
    Sets new password for logged-in user.
    """
    await controllers.user_set_password_v2(user_id=current_user.id, password=password, token=token)
