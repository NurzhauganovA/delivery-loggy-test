
class BaseUpdateOrderDeliveryPointError(Exception):
    """Базовая ошибка контроллера обновления точки доставки"""


class RoleUnavailable(BaseUpdateOrderDeliveryPointError):
    """Передана неверная роль инициатора"""


class InvalidBody(BaseUpdateOrderDeliveryPointError):
    """Передана неверное тело запроса"""


class CantUpdateOrderStatus(BaseUpdateOrderDeliveryPointError):
    """Обновление недоступно на данном статусе"""
