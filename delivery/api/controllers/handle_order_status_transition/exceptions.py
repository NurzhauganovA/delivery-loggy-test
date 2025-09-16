

class BaseOrderStatusTransitionHandlerError(Exception):
    """Базовая ошибка контролера перехода заявки на другой статус"""


class StatusHandlerExecutionError(BaseOrderStatusTransitionHandlerError):
    """Ошибка исполнения обработчика конкретного статуса"""
