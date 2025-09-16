import asyncio
import smtplib

import loguru
from api.conf import conf
from api import schemas
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

from ..common import BaseNotificationService

email_backend = conf.email_backend

conf = ConnectionConfig(
    MAIL_USERNAME=email_backend.sender_email,
    MAIL_PASSWORD='XywijVKHjb8pdgyPUZHj',
    MAIL_FROM=email_backend.sender_email,
    MAIL_PORT=465,
    MAIL_SERVER=email_backend.smtp_server,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
)


class EmailNotificationService(BaseNotificationService):

    @staticmethod
    async def __send_mail(
        text: str, subject: str, email_to: EmailStr
    ) -> None:
        message = MessageSchema(
            subject=subject,
            recipients=[email_to, ],
            template_body=text,
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        try:
            await fm.send_message(message)
        except Exception as e:
            loguru.logger.info(e)

    async def send_message(
        self, requisites: str,
        message: str, current_user: schemas.UserCurrent = None,
        subject: str = None
    ):
        await self.__send_mail(text=message, email_to=requisites, subject=subject)
