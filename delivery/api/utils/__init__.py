import asyncio
import functools
import math
import typing

import aiohttp
import fastapi
import pydantic
import tortoise

import api

from api import enums

T = typing.TypeVar('T')


class PaginationResponse(pydantic.BaseModel, typing.Generic[T]):
    items: typing.Sequence[T]
    current_page: int
    total_pages: int
    total: int


class PaginationParams:
    def __init__(
        self,
        page: int = fastapi.Query(default=1, gt=0),
        page_limit: int = fastapi.Query(default=10),
    ):
        self.page = page
        self.page_limit = page_limit

    def to_limit_offset_params(self):
        return self.page_limit, (self.page - 1) * self.page_limit


def as_dict(
    from_model: bool = False,
    exclude: typing.Optional[list] = None,
    record: typing.Optional[typing.Union[tortoise.models.Model,
                                         typing.List[tortoise.models.Model]]] = None,
) -> typing.Union[typing.Callable, dict, typing.List[dict]]:
    """Decorator to convert resulting model return into readable dict, or list of dicts."""

    def parse(_record: tortoise.models.Model) -> dict:
        result = {}
        for key, value in _record:
            if exclude is None:
                result[key] = value
            else:
                if key not in exclude:
                    result[key] = value

        return result

    def get_pagination_params(*args):
        for arg in args:
            if isinstance(arg, PaginationParams):
                return arg

    def get_pagination_result(params: PaginationParams, objects: list):
        if isinstance(objects, list):
            if len(objects) > 0:
                pages_count = math.ceil(len(objects) / params.page_limit)
            else:
                pages_count = 0

            return {
                'current_page': params.page,
                'total_pages': pages_count,
                'total': len(objects),
            }

    if record is not None:
        # If record is passed immediately return parsed result
        if isinstance(record, list):
            objects = []
            for rec in record:
                objects.append(parse(rec))
            return objects
        return parse(record)

    def inner(call: typing.Callable) -> typing.Callable:
        @functools.wraps(call)
        async def wrapped(*args, **kwargs) -> typing.Union[dict, list]:
            result = {}
            pagination_result = None
            record_from = await call(*args, **kwargs)

            if from_model:
                if isinstance(record_from, list):
                    result = []

                    pagination_params = get_pagination_params(*args)
                    if pagination_params is not None:
                        pagination_result = get_pagination_result(
                            pagination_params, record_from,
                        )

                    if pagination_params is not None:
                        limit, offset = pagination_params.to_limit_offset_params()
                        record_from = record_from[offset:offset + limit]

                    for model in record_from:
                        if exclude is None:
                            result.append(dict(model))
                        else:
                            result.append(
                                {
                                    key: value for key, value in dict(model).items()
                                    if key not in exclude
                                },
                            )

                    if pagination_result is not None:
                        result = {
                            **pagination_result,
                            'items': result,
                        }

                    return result
                result = parse(record_from)
            else:
                if record_from:
                    *_, result = record_from

            return result

        return wrapped

    return inner


def save_in_history(
    request_method: api.enums.RequestMethods,
    model_type: enums.HistoryModelName,
    initiator_type: enums.InitiatorType = enums.InitiatorType.USER
):
    """
    Takes function results and current user and creates History object.
    !!! You must provide current_user to repository method and history will be created successfully

    Function results must be only list, dict or None.

    action_data must be None e.g. for DELETE requests with 204 status code response.
    """

    def inner(func: typing.Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> typing.Union[dict, list]:
            current_user = kwargs.get('current_user')
            result = await func(*args, **kwargs)

            if result and not isinstance(result, dict):
                result = as_dict(record=result)

                if isinstance(result, list):
                    result = result[0]

            if current_user is not None:
                schema = api.schemas.HistoryCreate(
                    initiator_type=initiator_type,
                    initiator_id=current_user.id,
                    initiator_role=current_user.profile['profile_type'],
                    request_method=request_method,
                    model_type=model_type,
                    model_id=result.get('id') if result and not isinstance(result,
                                                                           list) else None
                )
                await api.models.history_create(schema)

            return result

        return wrapper

    return inner


async def send_link(
    body: [api.schemas.SendLink, api.schemas.SendLinkFeedback, api.schemas.SendLinkMonitoring],
    action: api.enums.SMSActions,
    current_user: [api.schemas.UserCurrent, None],
):
    if action == api.enums.SMSActions.FEEDBACK:
        message = action.format(body.receiver_name,
                                body.link,
                                )
    elif action == api.enums.SMSActions.MONITORING:
        message = action.format(body.receiver_name,
                                body.product_name,
                                body.partner_name,
                                body.link,
                                )
    else:
        message = action.format(body.link)
    try:
        api.services.sms.notification_service.send_message(
            body.phone_number,
            message,
            current_user
        ),
    except api.services.sms.SMSRemoteServiceResponseError as e:
        raise api.exceptions.HTTPBadRequestException(str(e)) from e
    except (
        asyncio.TimeoutError,
        aiohttp.ClientConnectorError,
        api.services.sms.SMSRemoteServiceRequestError,
    ) as e:
        raise api.exceptions.HTTPTemporarilyUnavailableException(str(e)) from e
