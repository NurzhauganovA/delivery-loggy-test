

class BasePOSTerminalAdapterError(Exception):
    """Базовый класс ошибки для адаптера POS Terminal"""
    pass


class POSTerminalAdapterValidationError(BasePOSTerminalAdapterError):
    """Ошибка валидации входных параметров"""
    pass


class POSTerminalAdapterBadRequestError(BasePOSTerminalAdapterError):
    """Ошибка при получении 4xx или 5xx HTTP кода ошибки"""
    pass