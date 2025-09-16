from ...common import BaseIntegrityError, BaseNotFoundError


class OrderChainNotFoundError(BaseNotFoundError):
    """Raises if partner order chain with provided ID does not exist."""

    code = 'oc1'


class OrderChainIntegrityError(BaseIntegrityError):
    """Raises if partner order chain with provided ID does not exist."""

    code = 'oc2'


class OrderChainStageNotFoundError(BaseNotFoundError):
    """Raises if partner order chain stage with provided ID does not exist."""

    code = 'ocs1'


class OrderChainStageIntegrityError(BaseIntegrityError):
    """Raises if partner order chain with provided ID does not exist."""

    code = 'ocs2'


class OrderChainReceiverNotFoundError(BaseNotFoundError):
    """Raises if partner order chain stage with provided ID does not exist."""

    code = 'ocr1'


class OrderChainReceiverIntegrityError(BaseIntegrityError):
    """Raises if partner order chain with provided ID does not exist."""

    code = 'ocr2'


class OrderChainSenderNotFoundError(BaseNotFoundError):
    """Raises if partner order chain stage with provided ID does not exist."""

    code = 'ocrse1'


class OrderChainSenderIntegrityError(BaseIntegrityError):
    """Raises if partner order chain with provided ID does not exist."""

    code = 'ocse2'


class OrderChainSupportDocumentNotFoundError(BaseNotFoundError):
    """Raises if partner order chain stage with provided ID does not exist."""

    code = 'ocsd1'


class OrderChainSupportDocumentIntegrityError(BaseIntegrityError):
    """Raises if partner order chain with provided ID does not exist."""

    code = 'ocsd2'
