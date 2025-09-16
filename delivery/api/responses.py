# TODO: add all necessary endpoint depending statuses
import enum

import fastapi
import pydantic


class Status(str, enum.Enum):
    @classmethod
    def get_status_string_values(cls) -> list:
        return [status.value for status in cls]


class CreatedStatus(Status):
    CREATED = 'created'


class NotImplementedStatus(Status):
    NOT_IMPLEMENTED = 'not_implemented'


class NoContentStatus(Status):
    NO_CONTENT = 'no_content'


class BadRequestStatus(Status):
    BAD_REQUEST = 'bad_request'


class UnauthenticatedStatus(Status):
    UNAUTHENTICATED = 'unauthenticated'


class UnauthorizedStatus(Status):
    UNAUTHORIZED = 'unauthorized'


class NotFoundStatus(Status):
    NOT_FOUND = 'not_found'


class TooManyRequestsStatus(Status):
    TOO_MANY_REQUESTS = 'too_many_requests'


class InternalErrorStatus(Status):
    INTERNAL_ERROR = 'internal_error'


class TemporarilyUnavailableStatus(Status):
    TEMPORARILY_UNAVAILABLE = 'temporarily_unavailable'


class APIResponse(pydantic.BaseModel):
    status: Status
    status_code: int
    detail: str

    @pydantic.validator('status_code')
    def _validate_status_code(cls, value: int) -> int:
        if not (200 <= value <= 599):
            raise ValueError('Invalid status code. Should be in range of 200 and 599')

        return value

    @classmethod
    def get_status_code(cls) -> int:
        return cls.__fields__['status_code'].default

    @classmethod
    def generate_schema(cls) -> dict:
        return {
            'application/json': {
                'example': {
                    'detail': 'string',
                    'status': {
                        'type': 'string',
                        'enum': cls.__fields__['status'].type_.get_status_string_values(),
                    },
                    'status_code': {
                        'type': 'int',
                        'default': cls.get_status_code(),
                    },
                },
            },
        }


class APIResponseCreated(APIResponse):
    status: CreatedStatus = CreatedStatus.CREATED
    status_code: int = 201


class APIResponseNoContent(APIResponse):
    status: NoContentStatus = NoContentStatus.NO_CONTENT
    status_code: int = 204


class APIResponseBadRequest(APIResponse):
    status: BadRequestStatus = BadRequestStatus.BAD_REQUEST
    status_code: int = 400


class APIResponseUnauthenticated(APIResponse):
    status: UnauthenticatedStatus = UnauthenticatedStatus.UNAUTHENTICATED
    status_code: int = 401


class APIResponseUnauthorized(APIResponse):
    status: UnauthorizedStatus = UnauthorizedStatus.UNAUTHORIZED
    status_code: int = 403


class APIResponseNotFound(APIResponse):
    status: NotFoundStatus = NotFoundStatus.NOT_FOUND
    status_code: int = 404


class APIResponseTooManyRequests(APIResponse):
    status: TooManyRequestsStatus = TooManyRequestsStatus.TOO_MANY_REQUESTS
    status_code: int = 429


class APIResponseInternalError(APIResponse):
    status: InternalErrorStatus = InternalErrorStatus.INTERNAL_ERROR
    status_code: int = 500


class APIResponseTemporarilyUnavailable(APIResponse):
    status: TemporarilyUnavailableStatus = (
        TemporarilyUnavailableStatus.TEMPORARILY_UNAVAILABLE
    )
    status_code: int = 503


def generate_responses(_: list) -> dict:
    return {}


def make_error_responses(include: list[int]) -> dict:
    all_responses = {
        400: {"description": "Bad Request", "model": APIResponseBadRequest},
        401: {"description": "Unauthenticated", "model": APIResponseUnauthenticated},
        403: {"description": "Unauthorized", "model": APIResponseUnauthorized},
        404: {"description": "Not Found", "model": APIResponseNotFound},
        500: {"description": "Internal Service Error", "model": APIResponseInternalError},
    }
    return {code: all_responses[code] for code in include if all_responses.get(code)}
