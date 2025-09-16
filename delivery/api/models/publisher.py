"""
    Временно вынес публикацию событий сюда для удобства использования.
    Это не целевое решение.
"""
import json

from api import redis_module


async def publish_callback(
        task_name: str,
        url: str,
        data: dict,
        headers: dict = None,
) -> None:
    message = {
        'task_name': task_name,
        'kwargs': {
            'url': url,
            'data': data,
            'headers': headers,
        },
    }
    await __publish(
        channel='send-to-celery',
        message=message,
    )


async def call_task(
        task_name: str,
        data: dict
) -> None:
    message = {
        'task_name': task_name,
        'kwargs': data,
    }
    await __publish(
        channel='send-to-celery',
        message=message,
    )


async def __publish(channel: str, message: dict) -> None:
    conn = redis_module.get_connection()
    await conn.publish(
        channel=channel,
        message=json.dumps(message)
    )
