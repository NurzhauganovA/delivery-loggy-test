from ...common import BaseIntegrityError, BaseNotFoundError


class OrderGroupNotFoundError(BaseNotFoundError):
    """Raises if partner shipment point with provided ID does not exist."""

    code = 'og1'


class OrderGroupIntegrityError(BaseIntegrityError):
    """Raises if partner shipment point with provided ID does not exist."""

    code = 'og2'
