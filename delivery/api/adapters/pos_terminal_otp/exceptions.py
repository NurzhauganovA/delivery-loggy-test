

class BaseOTPError(Exception):
    """Базовый класс ошибки для ОТП"""
    pass


class OTPValidationError(BaseOTPError):
    """Ошибка валидации входных параметров"""
    pass


class OTPBadRequestError(BaseOTPError):
    """Ошибка при получении 4xx или 5xx HTTP кода ошибки"""
    pass


class OTPInvalidOTPCode(BaseOTPError):
    """Ошибка при вводе неправильного ОТП кода"""
    pass
