

class BaseOrderDomainError(Exception):
    pass


class OrderValidationError(BaseOrderDomainError):
    """Ошибка валидации"""


class OrderTransitionError(BaseOrderDomainError):
    """Ошибка при переходе на невалидный статус"""


class DeliveryGraphValidationError(BaseOrderDomainError):
    """Ошибка валидации"""
