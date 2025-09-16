from decimal import Decimal, ROUND_DOWN

from pydantic import BaseModel, validator


class Money(BaseModel):
    amount: Decimal

    @validator('amount')
    def normalize_amount(cls, value: Decimal) -> Decimal:
        """Приводим значение к стоимости тенге с тиынами"""
        return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    @validator('amount')
    def validate_amount(cls, value: Decimal) -> Decimal:
        """Валидация значения amount"""
        if len(value.as_tuple().digits) > 10:
            raise ValueError('amount is too large')

        return value
