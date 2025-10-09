import sys
import json
import multipart

from loguru import logger
from typing import Any

# Удаление старых форматов вывода логов
logger.remove()

# Формат логирования
__FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level} | "
    "{name}:{function}:{line} - "
    "{message} | "
    "{extra}"
)


def exclude_logfilter(record):
    filter_params = (
        '/api/v1/openapi.json',
        '/api/v1/token/refresh',
        'OPTIONS',
    )
    return any(filter_param not in str(record) for filter_param in filter_params)


# Добавление кастомных форматов вывода логов:
# level: INFO
logger.add(
    sys.stdout,
    format=__FORMAT,
    level='INFO',
    filter=exclude_logfilter,
    enqueue=True,
)


def body_to_dict(content_type: str, data: Any) -> dict:
    """
    Перевод тела в dict формат

    Args:
        content_type: строка определяющая тип контента
        data: даныне полученные при запросе

    Returns":
        Данные переведённые в dict
        grant_type=password&username=123&password=123&scope=&client_id=&client_secret=
    """

    def urlencoded(data: str) -> dict:
        body = {}
        elements = data.split('&')
        for element in elements:
            key, value = element.split('=')
            body[key] = value
        return body

    def to_json(data: str) -> dict:
        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError:
            return {}

    if isinstance(data, bytes):
        try:
            data = data.decode('utf8')
        except UnicodeDecodeError:
            return {}
    if content_type == 'application/json':
        return to_json(data)
    if content_type == 'application/x-www-form-urlencoded':
        return urlencoded(data)
    return {}


def censore_fields(data: dict) -> dict:
    """
    Цензурирование полей из запроса

    Args:
        data: данные из запроса
        {
            "password": "12345",
            "image": b"a1b2c3d4e5",
            "phone": "+71234567890"
        }
    Returns:
        Данные с цензурой
        {
            "password": "***",
            "image": "***",
            "phone": "+71234567890"
        }
    """

    fields = (
        'password',
        'image',
        'refresh_token',
        'access_token',
    )

    def _mask_data(data_copy: dict) -> dict:
        if not isinstance(data_copy, dict):
            return data_copy
        for field in fields:
            if data_copy.get(field):
                data_copy[field] = '***'
        return data_copy

    if isinstance(data, dict):
        data_copy = data.copy()
        return _mask_data(data_copy)
    if isinstance(data, list):
        data_copy = data.copy()
        return [_mask_data(element) for element in data_copy]
    return data


def get_log_headers(headers: dict) -> dict:
    """
    Получение необходимых заголовков запроса для логов

    Args:
        headers: все логи полученные при запросе

    Returns:
        Необходимые заголовки запроса для логов
    """

    fields = (
        'user-agent',
    )
    log_headers = {headers.get(field) for field in fields}
    return log_headers
