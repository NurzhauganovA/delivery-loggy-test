from decimal import Decimal
from typing import Protocol, Optional


class POSTerminalAdapterProtocol(Protocol):
    async def registrate_pos_terminal(
            self,
            serial_number: str,
            model: str,
            merchant_id: str,
            terminal_id: str,
            receiver_iin: str,
            store_name: str,
            store_address: str,
            branch_name: str,
            oked_code: str,
            mcc_code: str,
            receiver_phone_number: str,
            receiver_full_name: str,
            courier_full_name: str,
            is_installment_enabled: bool,
            request_number_ref: Optional[str],
            inventory_number: Optional[str],
            sum: Optional[Decimal],
    ) -> str:
        ...
