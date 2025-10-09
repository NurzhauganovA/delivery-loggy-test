import time
from typing import Callable, Awaitable, Dict, Any
from api.logging_module import (
    logger,
    body_to_dict,
    censore_fields,
)


class LogMiddleware:
    def __init__(self, app, max_body: int = 1024 * 1024):
        self.app = app
        self.max_body = max_body

    def _extract_request_body(self, headers: Dict[str, str], body_parts: list[bytes]) -> dict:
        raw_body = b"".join(body_parts)
        return censore_fields(body_to_dict(headers.get("content-type"), raw_body))

    def _extract_response_body(self, resp_headers: Dict[str, str], resp_parts: list[bytes], is_streaming: bool) -> str:
        if is_streaming:
            return "<bytes>"
        try:
            resp_raw = b"".join(resp_parts)
            return resp_raw.decode("utf-8", errors="replace")
        except Exception:
            return "<bytes>"

    def _get_log_func(self, status: int):
        if status >= 500:
            return logger.error
        if status >= 400:
            return logger.warning
        return logger.info

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start_time = time.perf_counter()

        method = scope["method"]
        path = scope["path"]
        headers = {k.decode(): v.decode() for k, v in scope["headers"]}
        req_body_parts, resp_body_parts = [], []
        status_holder, resp_headers, resp_is_streaming = {}, {}, False

        async def recv_wrapper():
            message = await receive()
            if message["type"] == "http.request":
                chunk = message.get("body", b"")
                if chunk and sum(len(p) for p in req_body_parts) < self.max_body:
                    req_body_parts.append(chunk)
            return message

        async def send_wrapper(message: Dict[str, Any]):
            nonlocal resp_is_streaming
            if message["type"] == "http.response.start":
                status_holder["status"] = message["status"]
                resp_headers.update({k.decode(): v.decode() for k, v in message.get("headers", [])})
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                if message.get("more_body", False):
                    resp_is_streaming = True
                if body and not resp_is_streaming:
                    if sum(len(p) for p in resp_body_parts) < self.max_body:
                        resp_body_parts.append(body)
            await send(message)

        try:
            await self.app(scope, recv_wrapper, send_wrapper)
        finally:
            elapsed = time.perf_counter() - start_time

            req_body = self._extract_request_body(headers, req_body_parts)
            resp_body_log = self._extract_response_body(resp_headers, resp_body_parts, resp_is_streaming)

            status = status_holder.get("status")
            log_func = self._get_log_func(status)

            log_func(
                "http_access",
                method=method,
                url=path,
                status=status,
                user_agent=headers.get("user-agent"),
                profiles=headers.get("profiles"),
                body=req_body,
                resp_body=resp_body_log,
                finished_in=f"{elapsed:.3f} sec",
            )
