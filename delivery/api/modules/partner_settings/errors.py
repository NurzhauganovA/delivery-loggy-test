from ...common import BaseIntegrityError, BaseNotFoundError


class PartnerSettingPointNotFoundError(BaseNotFoundError):
    """Raises if partner settings with provided ID does not exist."""

    code = 'ps1'


class PartnerSettingIntegrityError(BaseIntegrityError):
    """Raises if partner settings with provided ID already exist."""

    code = 'ps2'
