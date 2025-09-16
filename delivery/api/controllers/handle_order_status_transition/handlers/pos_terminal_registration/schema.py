from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, constr, validator

from api.domain.money.money import Money


class POSTerminalModel(str, Enum):
    PAX = 'PAX'
    SUNMI = 'SUNMI'


class POSTerminalRegistrationData(BaseModel):
    model: POSTerminalModel
    serial_number: constr(min_length=1, max_length=20)
    inventory_number: Optional[constr(min_length=1, max_length=50)]
    sum: Optional[Decimal]

    @validator('sum')
    def validate_sum(cls, value: Decimal | None) -> Decimal | None:
        """Валидация значения sum"""
        if not value:
            return value

        try:
            money = Money(amount=value)
        except ValueError:
            raise ValueError('sum is too large')

        return money.amount
