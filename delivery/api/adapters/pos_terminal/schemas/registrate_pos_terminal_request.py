from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, validator


class POSTerminalRegistrationRequest(BaseModel):
    serial_number: str
    model: str
    merchant_id: str
    terminal_id: str
    receiver_iin: str
    store_name: str
    store_address: str
    branch_name: str
    oked_code: str
    mcc_code: str
    receiver_phone_number: str
    receiver_full_name: str
    courier_full_name: str
    request_number_ref: Optional[str]
    is_installment_enabled: bool

    @validator(
        'serial_number', 'model', 'merchant_id', 'terminal_id', 'receiver_iin',
        'store_name', 'store_address', 'branch_name', 'oked_code', 'mcc_code',
        'receiver_phone_number', 'receiver_full_name', 'courier_full_name'
    )
    def must_not_be_empty(cls, v, field):
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f'{field.name} is required')
        return v
