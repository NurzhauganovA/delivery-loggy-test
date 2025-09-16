
class BaseExternalOrderCreateException(Exception):
    pass


class ExternalOrderCreateDuplicateError(BaseExternalOrderCreateException):
    """Ошибка при обнаружении дубликата заказа у партнера"""

