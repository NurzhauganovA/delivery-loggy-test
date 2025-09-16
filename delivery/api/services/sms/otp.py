import asyncio
import json
import random

import loguru

from .sms import get_sms_service, get_email_service
from .. import common
from ... import services
from ...conf import conf
from ... import schemas


email_otp_template = """
<div style="font-family:Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2"><div style="margin:50px auto;width:70%;padding:20px 0"><div style="border-bottom:1px solid #eee"><a href="https://loggy.kz" style="font-size:1.4em;color:#00466a;text-decoration:none;font-weight:600"><img style="width:30%" src="https://loggy.kz/logo-dark.png" alt=""></a></div><p style="font-size:1.1em">Здравствуйте,</p><p>Спасибо за выбор Loggy. Вы можете использовать полученный OTP код в течении 5 минут</p><h2 style="background:#00466a;margin:0 auto;width:max-content;padding:0 10px;color:#fff;border-radius:4px">{otpcode}</h2><p style="font-size:.9em">Всего доброго,<br>Loggy</p><hr style="border:none;border-top:1px solid #eee"><div style="float:right;padding:8px 0;color:#aaa;font-size:.8em;line-height:1;font-weight:300"><p>Loggy Inc</p><p>Almaty, Jibek-Joly 135/3</p><p>Kazakstan</p></div></div></div>
"""


email_verification_template = """
<div style="font-family:Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2"><div style="margin:50px auto;width:70%;padding:20px 0"><div style="border-bottom:1px solid #eee"><a href="https://loggy.kz" style="font-size:1.4em;color:#00466a;text-decoration:none;font-weight:600"><img style="width:30%" src="https://loggy.kz/logo-dark.png" alt=""></a></div><p style="font-size:1.1em">Здравствуйте,</p><p>Спасибо за выбор Loggy. Вы можете использовать полученный OTP код в течении 10 минут. Полученный код необходимо ввести в поле которое должно появиться у вас после подтверждения смены email адреса</p><h2 style="background:#00466a;margin:0 auto;width:max-content;padding:0 10px;color:#fff;border-radius:4px">{otpcode}</h2><p style="font-size:.9em">Всего доброго,<br>Loggy</p><hr style="border:none;border-top:1px solid #eee"><div style="float:right;padding:8px 0;color:#aaa;font-size:.8em;line-height:1;font-weight:300"><p>Loggy Inc</p><p>Almaty, Jibek-Joly 135/3</p><p>Kazakstan</p></div></div></div>
"""

class OTP:
    def __init__(self):
        self.redis_service = common.RedisService()
        self.sms_service = get_sms_service(sms_service_type=conf.api.main_sms_service_type)
        self.email_service = get_email_service()

    @staticmethod
    def _make_message_with_otp_code(message: str, otp_code: int | None = None) -> tuple:
        if otp_code is None:
            otp_code = random.randint(1000, 9999)
        return message.format(otp_code), otp_code

    async def send_otp(
        self,
        phone_number: str,
        otp_code,
        current_user: schemas.UserCurrent = None,
    ) -> None:
        message, otp_code = self._make_message_with_otp_code(
            message='Код: {} - подтверждение номера телефона.',
            otp_code=otp_code,
        )
        if self.sms_service:
            await asyncio.wait_for(
                self.sms_service.send_message(phone_number, message, current_user),
                timeout=conf.otp.service_call_timeout,
            )
        else:
            otp_code = 1111

        await self.redis_service.set(
            f"otp_{phone_number}", otp_code, conf.api.otp_expiration_time
        )
        otp_exists = await self.redis_service.exists(f"otp_{phone_number}")
        if not otp_exists:
            loguru.logger.error('Otp was not added to redis')
        else:
            loguru.logger.debug('Otp was added to redis')

        return otp_code

    async def send_email_otp(
        self,
        email: str,
        otp_code,
        current_user: schemas.UserCurrent = None,
    ) -> None:
        message = email_otp_template.format(otpcode=otp_code)
        if self.email_service:
            await asyncio.wait_for(
                self.email_service.send_message(
                    requisites=email, message=message, subject='OTP код loggy.kz'
                ),
                timeout=conf.otp.service_call_timeout,
            )
        else:
            otp_code = 1111

        await self.redis_service.set(
            f"otp_{email}", otp_code, conf.api.otp_expiration_time
        )
        otp_exists = await self.redis_service.exists(f"otp_{email}")
        if not otp_exists:
            loguru.logger.error('Otp was not added to redis')
        else:
            loguru.logger.debug('Otp was added to redis')

        return otp_code

    async def send_email_verification_otp(
        self,
        email: str,
        otp_code,
        user_id: int,
    ) -> None:
        message = email_verification_template.format(otpcode=otp_code)
        if self.email_service:
            await asyncio.wait_for(
                self.email_service.send_message(
                    requisites=email,
                    message=message, subject='Подтверждение почтового адреса. loggy.kz'
                ),
                timeout=conf.otp.service_call_timeout,
            )
        else:
            otp_code = "1111"

        await self.redis_service.set(
            f"otp_{user_id}",
            json.dumps({"code": otp_code, "email": email}),
            600
        )
        otp_exists = await self.redis_service.exists(f"otp_{user_id}")
        if not otp_exists:
            loguru.logger.error('Otp was not added to redis')
        else:
            loguru.logger.debug('Otp was added to redis')

        return otp_code

    async def send_postcontrol_otp(
        self,
        phone_number: str,
        current_user: schemas.UserCurrent = None,
        otp_code: int | None = None,
    ) -> int:
        self.sms_service = get_sms_service(conf.api.postcontrol_sms_service_type)
        message, otp_code = self._make_message_with_otp_code(
            message='Ваш код: {}. Сообщите его курьеру для получения посылки.',
            otp_code=otp_code,
        )

        if self.sms_service:
            try:
                await asyncio.wait_for(
                    self.sms_service.send_message(phone_number, message, current_user),
                    timeout=conf.otp.service_call_timeout,
                )
            except asyncio.TimeoutError:
                raise services.sms.SMSRemoteServiceRequestError('SMS service is unavailable')
        else:
            otp_code = 1111

        return otp_code

    async def check_email_otp(self, user_id: int, otp: str):
        saved_otp = await self.redis_service.get(f"otp_{user_id}")

        if saved_otp:
            dict_otp = json.loads(saved_otp)
            if dict_otp['code'] == otp:
                return dict_otp['email']

    async def check_otp(self, key):
        return await self.redis_service.get(key)
