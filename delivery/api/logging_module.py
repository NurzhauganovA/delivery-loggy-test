import sys
from loguru import logger

# Удаление старых форматов вывода логов
logger.remove()

# Формат логирования
__FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level> | "
    "<level>{extra}</level>"
)

# Добавление кастомных форматов вывода логов:

# level: ERROR
logger.add(
    sys.stderr,
    format=__FORMAT,
    level='ERROR',
)
