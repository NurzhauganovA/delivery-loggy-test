from enum import Enum

from pydantic import (
    BaseModel,
    constr,
)


class POSTerminalModel(str, Enum):
    PAX = 'PAX'
    SUNMI = 'SUNMI'


class POSTerminalRegistrationData(BaseModel):
    model: POSTerminalModel
    serial_number: constr(min_length=1, max_length=20)
