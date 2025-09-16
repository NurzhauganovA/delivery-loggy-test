# TODO: shorten namings with `Exception` suffix
import typing

import starlette.exceptions
import starlette.status

from . import responses


class HTTPException(starlette.exceptions.HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: typing.Union[str, Exception],
        status: responses.Status,
    ) -> None:
        if not isinstance(detail, str):
            detail = str(detail)
        super().__init__(status_code, detail=detail)
        self.status = status


class HTTPUnauthenticatedException(HTTPException):
    """Raises on unauthenticated access."""

    def __init__(
        self,
        detail: typing.Union[str, Exception] = 'Unauthenticated access',
        status: responses.Status = responses.UnauthenticatedStatus.UNAUTHENTICATED,
    ) -> None:
        super().__init__(starlette.status.HTTP_401_UNAUTHORIZED, detail, status)
        self.headers = {'WWW-Authenticate': 'Bearer'}


class HTTPUnauthorizedException(HTTPException):
    """Raises on unauthorized access."""

    def __init__(
        self,
        detail: typing.Union[str, Exception] = 'Unauthorized access',
        status: responses.Status = responses.UnauthorizedStatus.UNAUTHORIZED,
    ) -> None:
        super().__init__(starlette.status.HTTP_403_FORBIDDEN, detail, status)


class HTTPNotImplemented(HTTPException):
    """Raises when request is not implemented."""

    def __init__(
        self,
        detail: typing.Union[str, Exception] = 'Not implemented',
        status: typing.Type[responses.Status] = responses.NotImplementedStatus.NOT_IMPLEMENTED
    ) -> None:
        super().__init__(starlette.status.HTTP_501_NOT_IMPLEMENTED, detail, status)


class HTTPNotFoundException(HTTPException):
    """Raises when queried object was not found."""

    def __init__(
        self,
        detail: typing.Union[str, Exception] = 'Queried object is not found',
        status: responses.Status = responses.NotFoundStatus.NOT_FOUND,
    ) -> None:
        super().__init__(starlette.status.HTTP_404_NOT_FOUND, detail, status)


class HTTPBadRequestException(HTTPException):
    """Raises when client made an invalid request."""

    def __init__(
        self,
        detail: typing.Union[str, Exception] = 'Request is invalid',
        status: responses.Status = responses.BadRequestStatus.BAD_REQUEST,
    ):
        super().__init__(starlette.status.HTTP_400_BAD_REQUEST, detail, status)


class HTTPHardCodeException(HTTPException):
    """Raises when client made an invalid request."""

    def __init__(
        self,
        detail: typing.Union[str, Exception] = 'Request is invalid',
        status: responses.Status = responses.BadRequestStatus.BAD_REQUEST,
    ):
        super().__init__(starlette.status.HTTP_409_CONFLICT, detail, status)


class HTTPTemporarilyUnavailableException(HTTPException):
    """Raises if service is temporarily unavailable."""

    def __init__(
        self,
        detail: typing.Union[str, Exception] = 'Service unavailable',
        status: responses.Status = (
            responses.TemporarilyUnavailableStatus.TEMPORARILY_UNAVAILABLE
        ),
    ):
        super().__init__(starlette.status.HTTP_503_SERVICE_UNAVAILABLE, detail, status)


class PydanticException(ValueError):
    def __init__(self, errors):
        self.raw_errors = errors

    def errors(self):
        errors = []
        for error in self.raw_errors:
            errors.append(
                {
                    'loc': ['body', error[0]],
                    'msg': error[1],
                    'type': 'validation_error',
                }
            )
        return errors


def get_exception_msg(exception: Exception) -> str:
    try:
        main_exc = str(exception).split('DETAIL: ')[1]
    except IndexError:
        main_exc = str(exception)

    return main_exc.strip()
