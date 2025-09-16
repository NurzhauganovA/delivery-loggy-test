

class BaseOTPSendError(Exception):
    pass


class SendOTPValidationError(BaseOTPSendError):
    """Ошибка валидации входных параметров у обработчика статуса заявки"""


class SendOTPError(BaseOTPSendError):
    """Ошибка вызова интеграции, внешнего сервиса"""


class SendOTPPartnerNotFoundError(BaseOTPSendError):
    """Нет ОТП сервиса для партнера"""
