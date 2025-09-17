from typing import ClassVar


class BaseBuisnessException(Exception):
    """
    Базовый класс для отлова исключений в бизнес логике

    Обязательные поля:
        status_code: HTTP статус код
        status: слаг для некоторых чеков на фронте
    """

    status_code: ClassVar[int]
    status: ClassVar[str]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls in BaseBuisnessException:
            required_attributes = {
                'status_code': int,
                'status': str,
            }
            for attribute, attribute_type in required_attributes.items():
                if not isinstance(getattr(cls, attribute), attribute_type):
                    raise TypeError(
                        f'{cls.__name__} must define class '
                        f'attribute {attribute} in type {attribute_type}'
                    )
