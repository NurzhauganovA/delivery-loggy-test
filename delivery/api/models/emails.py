import smtplib

import loguru
from api.conf import conf
from tortoise import Model, fields

email_backend = conf.email_backend


def send_mail(text: str, email_to: str, email_from: str = email_backend.sender_email) -> None:
    try:
        server = smtplib.SMTP_SSL(email_backend.smtp_server, email_backend.port)
        server.login(email_backend.sender_email, email_backend.password)
        server.sendmail(
            msg=text, to_addrs=email_to, from_addr=email_from
        )
    except Exception as e:
        loguru.logger.error(f"Error while sending mail. Exc info: {e}")
    finally:
        server.quit()


class Email(Model):
    mail = fields.CharField(max_length=100, pk=True)

    class Meta:
        table = "email"

    @classmethod
    async def send_mails(cls, text: str):
        emails = await cls.all()
        for email in emails:
            send_mail(text, email)
