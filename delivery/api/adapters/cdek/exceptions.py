

class BaseCDEKError(Exception):
    """Базовая ошибка CDEK интеграции"""


class CDEKValidationError(BaseCDEKError):
    """Ошибка валидации входных параметров"""


class CDEKGetLocationError(BaseCDEKError):
    """Ошибка получения локации"""


class CDEKCreateOrderError(BaseCDEKError):
    """Ошибка создания заявки"""
