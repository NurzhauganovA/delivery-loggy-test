import time
import fastapi

from starlette.middleware.base import BaseHTTPMiddleware

from api.logging_module import(
    logger,
    body_to_dict,
    censore_fields,
    get_log_headers,
)


class LogMiddleware(BaseHTTPMiddleware):

    def __is_streaming_response(self, content_type):
        content_types = (
            'application/octet-stream',
            'application/ms-excel',
        )
        return content_type and content_type in content_types

    async def dispatch(self, request: fastapi.Request, call_next):
        body = await request.body()
        content_type = request.headers.get('content-type')
        request.state.body = body
        log_body = body_to_dict(content_type, body)
        log_body = censore_fields(log_body)
        log_headers = get_log_headers(request.headers)

        log_message = logger.bind(
            method=request.method,
            url=request.url.path,
            body=log_body,
            headers=log_headers,
            ip=request.client.host,
        )

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        request = fastapi.Request(request.scope, receive=receive)
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            finished_in = time.time() - start_time
            finished_in = f'{finished_in:0.3f} sec'
            log_message = log_message.bind(
                status_code=500,
                finished_in=finished_in,
            )
            log_document = f'EXC: {exc}'
            log_message.error(log_document)
            raise exc

        finished_in = (time.perf_counter() - start_time)
        finished_in = f'{finished_in:0.3f} sec'
        status_code = response.status_code

        log_message = log_message.bind(
            status_code=status_code,
            finished_in=finished_in,
        )

        content_type = response.headers.get('content-type')

        if not self.__is_streaming_response(content_type):
            resp_body = b""
            async for chunk in response.body_iterator:
                resp_body += chunk

            try:
                body_log = resp_body.decode('utf-8')
            except UnicodeDecodeError as exc:
                body_log = f'<binary decode error: {exc}'

            try:
                response_log = body_to_dict('application/json', body_log)
                body_log = censore_fields(response_log)
            except Exception:
                pass

            if status_code < 400:
                log_document = f'SUCCESS: {body_log}'
                log_message.info(log_document)
            else:
                log_document = f'ERROR: {body_log}'
                log_message.error(log_document)

            return fastapi.Response(
                content=resp_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        else:
            if status_code < 400:
                log_document = f'SUCCESS: <Streaming>'
                log_message.info(log_document)
            else:
                log_document = f'ERROR: <Streaming>'
                log_message.error(log_document)
            return response
