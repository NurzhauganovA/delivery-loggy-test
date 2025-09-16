

class BaseGetOrderProductException(Exception):
    pass


class OrderProductNotFoundError(BaseGetOrderProductException):
    """Ошибка, если не смогли найти такого продукта у такого заказа"""

