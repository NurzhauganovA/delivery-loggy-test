from .otp import OTP
from .notification import SMSNotification
from .sms import SMSRemoteServiceRequestError, get_sms_service, get_email_service
from .sms import SMSRemoteServiceResponseError

notification_service = SMSNotification()
otp_service = OTP()

__all__ = [
    'notification_service', 'otp_service',
    'SMSRemoteServiceRequestError', 'SMSRemoteServiceResponseError'
]
