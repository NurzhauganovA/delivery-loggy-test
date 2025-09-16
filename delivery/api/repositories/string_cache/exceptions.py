class BaseCacheError(Exception):
    """Базовый класс исключений при работе с кешем"""
    pass


class CacheGetValueError(BaseCacheError):
    """Ошибка при получении значения из кеша"""
    pass


class CacheSetValueError(BaseCacheError):
    """Ошибка при вставке значения в кеш"""
    pass


