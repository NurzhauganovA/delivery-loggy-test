from fastapi import Depends, Body
from pydantic import EmailStr

from api import models
from api.auth import get_current_user
from api.exceptions import HTTPBadRequestException
from api.schemas import UserCurrent


async def validate_email_for_change(
    email: EmailStr = Body(embed=True),
    current_user: UserCurrent = Depends(get_current_user),
):
    if await models.User.filter(id__not=current_user.id, email=email).exists():
        raise HTTPBadRequestException('this email belongs to another user')
    return email


__all__ = (
    'validate_email_for_change',
)
