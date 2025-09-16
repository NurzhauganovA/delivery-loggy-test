import asyncio

import aiohttp
import tortoise.transactions

from .. import enums
from .. import exceptions
from .. import models
from .. import schemas
from ..services import sms
from ..services.sms.notification import send_confirm_phone_otp


@tortoise.transactions.atomic()
async def register(owner: schemas.RegisterCreate) -> None:
    """Register owner of a partner.
    Create user, profile and send OTP. If error was
    raised than DB must be rollbacked.
    """
    try:
        user = await models.user_create(
            # UserCreate schemas should not support
            # assigned None values by default
            schemas.UserCreate(
                phone_number=owner.phone_number,
            ),
        )
    except models.ProfileAlreadyExists as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e

    try:
        await models.new_profile_create(
            schemas.ProfileCreate(
                user_id=user['id'],
                profile_type=enums.ProfileType.OWNER,
                profile_content=schemas.ProfileOwnerCreate(),
            ),
        )
    except models.ProfileAlreadyExists as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e

    try:
        otp_code = await models.utils.create_otp()
        await send_confirm_phone_otp(phone=owner.phone_number, otp_code=otp_code)
        # await sms.otp_service.send_otp(phone_number=owner.phone_number, otp_code=otp_code)
    except sms.SMSRemoteServiceResponseError as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except (
            asyncio.TimeoutError,
            aiohttp.ClientConnectorError,
            sms.SMSRemoteServiceRequestError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e
