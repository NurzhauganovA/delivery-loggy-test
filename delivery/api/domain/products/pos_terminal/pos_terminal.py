from enum import Enum
from typing import Optional


# Общий список статусов
class RegistrationStatus(str, Enum):
    COMPLETED = 'COMPLETED'
    ERROR = 'ERROR'
    CANCELED = 'CANCELED'
    STARTED = 'STARTED'
    TIMEOUT_ERROR = 'TIMEOUT_ERROR'
