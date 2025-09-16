import asyncio
import uuid
import zoneinfo
from datetime import datetime
from pathlib import Path

import aiohttp
import loguru
import pdfkit

from ..conf import conf
from .. import enums
from .. import exceptions
from .. import models
from .. import schemas
from ..schemas.otp import Email, PhoneNumber
from ..services import dataloader, sms
from ..services.sms.notification import send_confirm_phone_otp
from ..services.sms.notification import send_email_otp


async def check_user_can_authorize(user, body):
    if not user.is_active:
        raise exceptions.HTTPUnauthorizedException('You are blocked!')

    if body.type == enums.OTPType.REGISTER and user:
        raise exceptions.HTTPBadRequestException(
            'The phone number is already registered',
        )

    if body.type == enums.OTPType.AUTHORIZATION and not user:
        raise exceptions.HTTPNotFoundException(
            'User does not registered',
        )


async def send_otp_phone_number(body):
    try:
        # !hardcode
        if body.credentials.phone_number == '+77077393783':
            otp_code = 8542
        else:
            otp_code = await models.utils.create_otp()
        await send_confirm_phone_otp(body.credentials.phone_number, otp_code=otp_code)
        if conf.api.debug:
            await sms.otp_service.send_otp(body.credentials.phone_number, otp_code=otp_code)
    except sms.SMSRemoteServiceResponseError as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except (
        asyncio.TimeoutError,
        aiohttp.ClientConnectorError,
        sms.SMSRemoteServiceRequestError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(
            str(e)) from e
    except dataloader.DataloaderDontConfigured as e:
        raise exceptions.HTTPNotImplemented(str(e)) from e


async def send_otp_email(body):
    try:
        # !hardcode
        if body.credentials.email == 'jedelloggy@rambler.ru':
            otp_code = 8542
        else:
            otp_code = await models.utils.create_otp()
        await send_email_otp(body.credentials.email, otp_code=otp_code)
        if conf.api.debug:
            await sms.otp_service.send_email_otp(body.credentials.email, otp_code=otp_code)
    except sms.SMSRemoteServiceResponseError as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except (
        asyncio.TimeoutError,
        aiohttp.ClientConnectorError,
        sms.SMSRemoteServiceRequestError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(
            str(e)) from e
    except dataloader.DataloaderDontConfigured as e:
        raise exceptions.HTTPNotImplemented(str(e)) from e


async def otp_create(body: schemas.OTPCreate) -> dict:
    user = None
    try:
        if isinstance(body.credentials, Email):
            user = await models.user_get_by_email(
                email=body.credentials.email
            )
            await check_user_can_authorize(user, body)
            await send_otp_email(body)
        if isinstance(body.credentials, PhoneNumber):
            user = await models.user_get_by_phone_number(
                phone_number=body.credentials.phone_number
            )
            await check_user_can_authorize(user, body)
            await send_otp_phone_number(body)
            user = await models.user_get_by_phone_number(body.credentials.phone_number)
        if user:
            profiles = await models.get_all_user_profiles(user.id)
            return {"profiles": profiles}

    except models.UserNotFound as e:
        loguru.logger.debug(e)
        raise exceptions.HTTPNotFoundException(e)


async def otp_validate(
    phone_number: str, password: str, agree: bool = False, bg_tasks=None,
):
    try:
        user = await models.user_get_by_phone_number(phone_number)
        if agree:
            user_data = {
                'last_name': "asdfasdf",
                'first_name': "asdfasdf",
                'middle_name': "asdfasdf",

            }
            last_name = user_data['last_name']
            first_name = user_data['first_name']
            middle_name = user_data.get('middle_name')
            fullname = f"{last_name} {first_name} {middle_name or ''}"
            fullname = fullname.strip()
            current_time = datetime.now().astimezone(
                zoneinfo.ZoneInfo(
                    key='Asia/Almaty')).strftime('%Y-%m-%d, %H:%M:%S')

            bg_tasks.add_task(save_agreement, phone_number,
                              password, fullname, user.iin,
                              current_time=current_time)
    except models.UserNotFound as e:
        raise exceptions.HTTPNotFoundException(str(e)) from e
    except (
        dataloader.DataloaderRemoteServiceRequestError,
        dataloader.DataloaderRemoteServiceResponseError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e
    except dataloader.DataloaderDontConfigured as e:
        raise exceptions.HTTPNotImplemented(str(e)) from e
    password_stored = await sms.otp_service.check_otp(f'otp_{phone_number}')
    if password_stored is None:
        raise exceptions.HTTPNotFoundException('OTP not found')
    if password_stored != password:
        raise exceptions.HTTPBadRequestException('OTP not valid')


async def send_register_link(
    sms_request: schemas.Message,
    current_user: schemas.UserCurrent,
):
    try:
        # await sms.notification_service.send_message(
        #     phone_number=sms_request.phone_number,
        #     message=sms_request.message,
        #     current_user=current_user,
        # ),
        pass

    except sms.SMSRemoteServiceResponseError as e:
        raise exceptions.HTTPBadRequestException(str(e)) from e
    except (
        asyncio.TimeoutError,
        aiohttp.ClientConnectorError,
        sms.SMSRemoteServiceRequestError,
    ) as e:
        raise exceptions.HTTPTemporarilyUnavailableException(str(e)) from e
    except dataloader.DataloaderDontConfigured as e:
        raise exceptions.HTTPNotImplemented(str(e)) from e


async def save_agreement(
    phone_number: str, password: str, fullname, iin, current_time,
):
    template_path = conf.static.root / 'user_personal_agreement_template.html'
    css_path = conf.static.root / 'user_personal_agreement.css'

    if user := await models.User.filter(phone_number=phone_number).first():
        file_path = Path(user._meta.fields_map['personal_agreement'].upload_to) / f'{uuid.uuid4()}.pdf'
        full_path = conf.media.root / file_path

        with open(template_path, 'r') as template:
            html_text = template.read()
            generated = html_text.format(phone_number=phone_number,
                                         password=password,
                                         fullname=fullname,
                                         iin=iin,
                                         datetime=current_time,
                                         otp=password,
                                         )
            pdfkit.from_string(generated, full_path, css=css_path)
            user.personal_agreement = str(file_path)
            await user.save()
