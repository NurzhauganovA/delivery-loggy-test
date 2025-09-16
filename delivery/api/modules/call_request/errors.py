from api.common.error_base import BaseIntegrityError
from api.common.error_base import BaseNotFoundError


class CallRequestNotFoundError(BaseNotFoundError):
    """Raises when call request entity not found."""


class CallRequestIntegrityError(BaseIntegrityError):
    """Raises when call request integrity error occurred"""


class CallRequestContactNotFoundError(BaseNotFoundError):
    """Raises when call request contact entity not found."""


class CallRequestContactIntegrityError(BaseIntegrityError):
    """Raises when call request contact integrity error occurred"""


__all__ = (
    'CallRequestContactIntegrityError',
    'CallRequestContactNotFoundError',
    'CallRequestIntegrityError',
    'CallRequestNotFoundError',
)
