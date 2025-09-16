from ...common import BaseIntegrityError, BaseNotFoundError


class PartnerShipmentPointNotFoundError(BaseNotFoundError):
    """Raises if partner shipment point with provided ID does not exist."""

    code = 'psp1'


class PartnerShipmentPointIntegrityError(BaseIntegrityError):
    """Raises if partner shipment point with provided ID does not exist."""

    code = 'psp2'
