
class BaseCDEKExeption(Exception):
    pass


class CDEKValidationError(BaseCDEKExeption):
    """Ошибка валидации у входных параметров адреса для СДЕК"""
