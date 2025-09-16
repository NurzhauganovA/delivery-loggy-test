

class BasePOSTerminalRegistrationHandlerError(Exception):
    pass


class POSTerminalRegistrationHandlerValidationError(BasePOSTerminalRegistrationHandlerError):
    """Ошибка валидации входных параметров у обработчика статуса заявки"""


class POSTerminalRegistrationHandlerIntegrationError(BasePOSTerminalRegistrationHandlerError):
    """Ошибка вызова интеграции, внешнего сервиса"""


class NotAllowPOSTerminalRegistration(BasePOSTerminalRegistrationHandlerError):
    """Ошибка, если не разрешили запускать регистрацию pos терминала по бизнес правилам"""
