import json


class BaseError(Exception):
    code = ''
    kwargs = None

    def __init__(self, table, detail, **kwargs):
        self.table = table
        self.detail = detail
        self.kwargs = kwargs
        self.kwargs['table'] = table


class BaseNotFoundError(BaseError):
    """Raises if Entity with provided ID not found."""
    ...


class BaseIntegrityError(BaseError):
    """Raises if Entity has creation or update conflict."""
    ...
