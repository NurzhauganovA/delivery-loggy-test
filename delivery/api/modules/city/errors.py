from api.common.error_base import BaseIntegrityError
from api.common.error_base import BaseNotFoundError


class CityNotFoundError(BaseNotFoundError):
    """Raises when city entity not found."""


class CityIntegrityError(BaseIntegrityError):
    """Raises when city integrity error occurred"""


__all__ = (
    'CityIntegrityError',
    'CityNotFoundError',
)
