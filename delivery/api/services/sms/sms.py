import json
import uuid
import abc

import aiohttp.client_exceptions
import loguru

from ..common import BaseNotificationService
from ..email.email import EmailNotificationService
from ... import enums
from ... import models
from ...conf import conf
from ... import schemas
from .. import common


class SMSRemoteServiceRequestError(Exception):
    """Raises when remote SMS service cannot proceed with request."""


class SMSRemoteServiceResponseError(Exception):
    """Raises when remote SMS service returns response with `ERROR` status."""


class SMSServiceType(enums.Descriptor):
    DATALOADER = 'dataloader'
    SMSTRAFFIC = 'smstraffic'
    NONE = 'none'




class NotificationServiceDev(BaseNotificationService):
    def __init__(
            self,
            main_url: str,
            headers: dict = None,
            reserve_url: str = None,
    ) -> None:
        super().__init__(headers)
        self.redis_service = common.RedisService()
        self.main_url = main_url
        self.reserve_url = main_url

    def _get_sms_data(self, phone_number: str, message: str) -> dict:
        return {
            'mobile_phone': phone_number,
            'subject_identifier': str(uuid.uuid4()),
            'message': message
        }

    async def send_message(
            self,
            requisites: str,
            message: str,
            current_user: schemas.UserCurrent = None,
    ):
        sms_data = self._get_sms_data(requisites, message)
        try:
            resp = await self._async_session.recorded_post(
                url=f'{self.main_url}',
                data=json.dumps(sms_data),
                initiator=current_user.id if current_user else None,
                max_retries=3,
            )
            data = await resp.json()
            loguru.logger.debug(str(data))
        except (
            aiohttp.client_exceptions.ClientError,
            aiohttp.client_exceptions.ClientConnectorError,
        ) as e:
            loguru.logger.error(str(e))
            raise SMSRemoteServiceRequestError('SMS service is unavailable')
        if not data:
            raise SMSRemoteServiceRequestError(
                f'Cannot send_otp message due to status code: {resp.status}',
            )
        if not resp.ok:
            try:
                raise SMSRemoteServiceResponseError(
                    data['detail'][0]['msg']
                )
            except (
                    IndexError, KeyError
            ):
                pass

        if current_user:
            try:
                user_to_register = await models.user_get(phone_number=requisites)
                history_schema = schemas.HistoryCreate(
                    initiator_type=enums.InitiatorType.USER,
                    initiator_id=current_user.id,
                    initiator_role=current_user.profile['profile_type'],
                    request_method=enums.RequestMethods.POST,
                    model_type=enums.HistoryModelName.USER,
                    model_id=user_to_register['id']
                )
                await models.history_create(history_schema)

            except models.UserNotFound:
                pass


class NotificationService(BaseNotificationService):
    def _get_sms_data(self, phone_number, message) -> dict:
        return {
            'login': conf.otp.credentials.smstraffic.login,
            'password': conf.otp.credentials.smstraffic.password,
            'phones': phone_number[1:],
            'rus': 5,
            'originator': conf.otp.sender,
            'message': message
        }

    async def send_message(
            self,
            requisites: str,
            message: str,
            current_user: schemas.UserCurrent = None,
    ):
        params = self._get_sms_data(requisites, message)
        resp = await self._async_session.recorded_post(
            f'{conf.otp.urls.sms_traffic_url}', params=params, initiator=current_user.id if current_user else None
        )
        loguru.logger.debug(resp.request_info)
        data = await resp.read()
        if not data:
            resp = await self._async_session.recorded_post(
                f'{conf.otp.urls.smstraffic_reserve_url}',
                params=params,
                initiator=current_user.id if current_user else None,
            )
            data = await resp.read()
            if not data:
                raise SMSRemoteServiceRequestError(
                    f'Cannot send_otp message due to status code: {resp.status}',
                )
        if data:
            loguru.logger.debug(str(data))
            if 'ERROR' in str(data):
                raise SMSRemoteServiceRequestError(
                    'SMS service is unavailable',
                )

        if current_user:
            try:
                user_to_register = await models.user_get(phone_number=requisites)
                history_schema = schemas.HistoryCreate(
                    initiator_type=enums.InitiatorType.USER,
                    initiator_id=current_user.id,
                    initiator_role=current_user.profile['profile_type'],
                    request_method=enums.RequestMethods.POST,
                    model_type=enums.HistoryModelName.USER,
                    model_id=user_to_register['id']
                )
                await models.history_create(history_schema)

            except models.UserNotFound:
                pass


def get_sms_service(sms_service_type: SMSServiceType):
    if not conf.api.allow_sms:
        return None
    else:
        if sms_service_type == SMSServiceType.DATALOADER:
            return NotificationServiceDev(
                headers={'Content-Type': 'application/json'},
                main_url=conf.otp.urls.dataloader_sms_url
            )
        elif sms_service_type == SMSServiceType.SMSTRAFFIC:
            return NotificationService(
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
            )


def get_email_service():
    if not conf.api.allow_emails:
        return None
    else:
        return EmailNotificationService()