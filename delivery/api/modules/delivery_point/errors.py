from ...common import BaseIntegrityError, BaseNotFoundError


class DeliveryPointNotFoundError(BaseNotFoundError):
    """Raises if delivery point with provided ID does not exist."""

    code = 'dp1'


class DeliveryPointIntegrityError(BaseIntegrityError):
    """Raises if delivery point with provided data already exist."""

    code = 'dp2'


__all__ = (
    'DeliveryPointIntegrityError',
    'DeliveryPointNotFoundError',
)
