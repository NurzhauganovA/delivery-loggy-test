import asyncio
import json

import aioredis
import loguru
from .sms import get_sms_service
from .. import common
from ...conf import conf
from ... import schemas, enums


class SMSNotification:
    def __init__(self):
        self.sms_service = get_sms_service(sms_service_type=conf.api.main_sms_service_type)

    async def send_message(
            self,
            message: str,
            phone_number: str,
            current_user: schemas.UserCurrent = None,
    ) -> None:
        if self.sms_service:
            await asyncio.wait_for(
                self.sms_service.send_message(
                    requisites=phone_number,
                    message=message,
                    current_user=current_user,
                ),
                timeout=conf.otp.service_call_timeout,
            )


async def send_message_to_notification_service(channel, data):
    """Send message to notification service"""
    redis = aioredis.from_url(conf.redis.uri)
    await redis.publish(channel, json.dumps(data))
    loguru.logger.debug({'channel': channel, 'data': data})


async def send_call_request(
    phone,
    email,
    potential_customer,
    language=enums.LanguageType.RU.value,
):
    channel = enums.ChannelType.CALL_REQUEST.value
    data = {
        'phone': phone,
        'email': email,
        'potential_customer': potential_customer,
        'lang': language,
    }
    await send_message_to_notification_service(channel, data)


async def send_feedback_link(
    phone,
    link,
    receiver_full_name=None,
    related_order_id=None,
    current_user_id=None,
    language=enums.LanguageType.RU.value
):
    """Send feedback link to clients through notification service"""
    if conf.api.allow_send_feedback_link:
        channel = enums.ChannelType.SEND_FEEDBACK_LINK.value
        data = {
            'phone': phone,
            'link': link,
            'receiver_full_name': receiver_full_name,
            'related_order_id': related_order_id,
            'sender_user_id': current_user_id,
            'lang': language
        }
        await send_message_to_notification_service(channel, data)


async def send_post_control_otp(
    phone,
    otp_code,
    receiver_full_name=None,
    related_order_id=None,
    current_user_id=None,
    language=enums.LanguageType.RU.value
):
    """Send post-control otp code through notification service"""
    channel = enums.ChannelType.SEND_POST_CONTROL_OTP.value
    data = {
        'phone': phone,
        'otp_code': otp_code,
        'receiver_full_name': receiver_full_name,
        'related_order_id': related_order_id,
        'sender_user_id': current_user_id,
        'lang': language
    }
    await send_message_to_notification_service(channel, data)


async def send_confirm_phone_otp(
    phone,
    otp_code,
    receiver_full_name=None,
    related_order_id=None,
    current_user_id=None,
    language=enums.LanguageType.RU.value
):
    """Send otp code for confirm phone through notification service"""
    channel = enums.ChannelType.SEND_CONFIRM_PHONE_OTP.value
    data = {
        'phone': phone,
        'otp_code': otp_code,
        'sender_user_id': current_user_id,
        'receiver_full_name': receiver_full_name,
        'related_order_id': related_order_id,
        'lang': language
    }
    await send_message_to_notification_service(channel, data)


async def send_confirm_email_otp(
    email,
    otp_code: str, user_id,
    receiver_full_name=None,
    related_order_id=None,
    language=enums.LanguageType.RU.value,
):
    """Send otp code for confirm email through notification service"""
    channel = enums.ChannelType.SEND_EMAIL_OTP
    data = {
        'email': email,
        'otp_code': otp_code,
        'sender_user_id': user_id,
        'receiver_full_name': receiver_full_name,
        'related_order_id': related_order_id,
        'lang': language,
    }
    redis_service = common.RedisService()
    await redis_service.set(
        f"otp_{user_id}",
        json.dumps({"code": otp_code, "email": email}),
        600
    )
    otp_exists = await redis_service.exists(f"otp_{user_id}")
    if not otp_exists:
        loguru.logger.error('Otp was not added to redis')
    else:
        loguru.logger.debug('Otp was added to redis')
    await send_message_to_notification_service(channel, data)


async def send_email_magic_link(
    email,
    magic_link: str,
    user_id,
    receiver_role: str,
    receiver_full_name=None,
    language=enums.LanguageType.RU.value,
):
    """Send otp code for confirm email through notification service"""
    channel = enums.ChannelType.SEND_EMAIL_MAGIC_LINK
    data = {
        'email': email,
        'magic_link': magic_link,
        'sender_user_id': user_id,
        'receiver_full_name': receiver_full_name,
        'receiver_role': receiver_role,
        'lang': language,
    }
    await send_message_to_notification_service(channel, data)


async def send_email_otp(
    email,
    otp_code,
    receiver_full_name=None,
    language=enums.LanguageType.RU.value,
):
    """Send otp code for confirm email through notification service"""
    channel = enums.ChannelType.SEND_EMAIL_OTP
    data = {
        'email': email,
        'otp_code': otp_code,
        'sender_user_id': None,
        'receiver_full_name': receiver_full_name,
        'related_order_id': None,
        'lang': language,
    }
    redis_service = common.RedisService()
    await redis_service.set(
        f"otp_{email}", str(otp_code),
        600
    )
    otp_exists = await redis_service.exists(f"otp_{email}")
    if not otp_exists:
        loguru.logger.error('Otp was not added to redis')
    else:
        loguru.logger.debug('Otp was added to redis')
    await send_message_to_notification_service(channel, data)


async def send_courier_assigned_notification(
    phone,
    message,
    receiver_full_name=None,
    related_order_id=None,
    sender_user_id=None,
    language=enums.LanguageType.RU.value
):
    """Send courier assigned notify to receiver through notification service"""
    channel = enums.ChannelType.SEND_COURIER_ASSIGNED_NOTIFICATION.value
    data = {
        'phone': phone,
        'message': message,
        'receiver_full_name': receiver_full_name,
        'related_order_id': related_order_id,
        'sender_user_id': sender_user_id,
        'lang': language
    }
    await send_message_to_notification_service(channel, data)
