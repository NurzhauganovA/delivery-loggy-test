import time
from functools import wraps

from httpx import (
    Response,
    RequestError,
    HTTPStatusError,
)
from loguru import logger


def log_client_request(client_name: str, method_name: str):
    """
        Декоратор-фабрика для полного логирования запроса к внешнему сервису.

        Args:
            client_name: Название клиента (слой clients)
            method_name: Название метода клиента

        Returns:
            Конкретную реализацию декоратора
    """

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            context_logger = logger.bind(
                client_name=client_name,
                method_name=method_name,
                kwargs=kwargs,
            )

            started_time = time.perf_counter()

            try:
                response: Response = await func(*args, **kwargs)
                response.raise_for_status()

            except RequestError as e:
                context_logger.bind(
                    finished_in=f"{time.perf_counter() - started_time:.3f} sec",
                ).exception(f"RequestError - {e}")
                raise e

            except HTTPStatusError as e:
                context_logger.bind(
                    status_code=e.response.status_code,
                    method=e.response.request.method,
                    url=str(e.response.url),
                    response=e.response.text,
                    finished_in=f"{time.perf_counter() - started_time:.3f} sec",
                ).error(f"HTTPStatusError - {e}")
                raise e

            except Exception as e:
                context_logger.bind(
                    finished_in=f"{time.perf_counter() - started_time:.3f} sec",
                ).exception(f"Unexpected error - {e}")
                raise e

            context_logger.bind(
                status_code=response.status_code,
                url=str(response.url),
                finished_in=f"{time.perf_counter() - started_time:.3f} sec",
            ).info("Success")

            return response

        return wrapper

    return decorator