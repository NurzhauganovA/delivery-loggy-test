import json
import time
import typing
import logging
from typing import Any
import fastapi.responses
import starlette.middleware.base
from api.responses import InternalErrorStatus
from fastapi import FastAPI
from starlette.responses import StreamingResponse
import traceback


class AsyncIteratorWrapper:
    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value


class InternalServerErrorHandlingMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    async def dispatch(
            self,
            request: fastapi.Request,
            call_next: typing.Callable,
    ) -> fastapi.responses.StreamingResponse | fastapi.responses.JSONResponse:
        try:
            return await call_next(request)
        except Exception:
            return fastapi.responses.JSONResponse(
                status_code=500,
                content={
                    'status': InternalErrorStatus.INTERNAL_ERROR,
                    'status_code': 500,
                }
            )


class RouterLoggingMiddleware(starlette.middleware.base.BaseHTTPMiddleware):

    def __init__(
            self,
            app: FastAPI,
            *,
            logger: logging.Logger,
            with_body: bool = False,
    ) -> None:
        self._logger = logger
        self._with_body = with_body
        super().__init__(app)

    async def dispatch(
            self,
            request: fastapi.Request,
            call_next: typing.Callable,
    ) -> fastapi.responses.StreamingResponse:

        logging_dict = {}

        start_time = time.perf_counter()

        response = await self._execute_request(
            call_next=call_next, request=request
        )

        finish_time = time.perf_counter()

        execution_time = finish_time - start_time

        if self._with_body:
            await self.set_body(request)

        if response:
            response_dict = await self._log_response(
                response=response, execution_time=execution_time
            )
            logging_dict["response"] = response_dict

        request_dict = await self._log_request(request)
        logging_dict["request"] = request_dict


        self._logger.info(logging_dict)

        return response

    @staticmethod
    async def set_body(request):
        receive_ = await request._receive()

        async def receive():
            return receive_

        request._receive = receive

    @staticmethod
    async def _log_request(
            request: fastapi.Request,
    ) -> dict[str, str | typing.Any]:
        path = request.url.path
        if request.query_params:
            path += f"?{request.query_params}"

        request_logging = {
            "method": request.method,
            "path": path,
            "ip": request.client.host,
            "user_agent": request.headers.get('User-Agent', '')
        }

        return request_logging

    async def _log_response(
            self,
            response: StreamingResponse,
            execution_time: time.time
    ) -> dict[str, str | int | Any]:
        overall_status = "successful" if response.status_code < 400 else "failed"

        response_logging = {
            "status": overall_status,
            "status_code": response.status_code,
            "time_taken": f"{execution_time:0.4f}s"
        }

        if overall_status == "failed":
            resp_body = [section async for section in response.__dict__["body_iterator"]]
            response.__setattr__("body_iterator", AsyncIteratorWrapper(resp_body))

            try:
                resp_body = json.loads(resp_body[0].decode())
            except:
                resp_body = str(resp_body)

            response_logging["body"] = resp_body

        return response_logging

    async def _execute_request(
            self,
            request: fastapi.Request,
            call_next: typing.Callable,
    ) -> fastapi.responses.StreamingResponse:
        try:
            return await call_next(request)
        except Exception as e:
            trace = traceback.format_exc()
            self._logger.exception(
                {
                    "path": request.url.path,
                    "method": request.method,
                    "reason": e,
                    "details": trace,
                    "user_agent": request.headers.get('User-Agent', '')
                }
            )
            raise