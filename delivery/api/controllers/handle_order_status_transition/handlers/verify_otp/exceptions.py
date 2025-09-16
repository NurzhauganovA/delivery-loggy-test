

class BaseOTPVerifyError(Exception):
    pass


class VerifyOTPValidationError(BaseOTPVerifyError):
    """Ошибка валидации входных параметров у обработчика статуса заявки"""


class VerifyOTPError(BaseOTPVerifyError):
    """Ошибка вызова интеграции, внешнего сервиса"""


class VerifyOTPWrongCodeError(BaseOTPVerifyError):
    """Ошибка вызова интеграции, внешнего сервиса"""


class VerifyOTPPartnerNotFoundError(BaseOTPVerifyError):
    """Нет ОТП сервиса для партнера"""
