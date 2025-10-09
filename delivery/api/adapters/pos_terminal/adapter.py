from decimal import Decimal
from typing import Optional

from httpx import (
    HTTPStatusError,
    RequestError,
)
from pydantic import ValidationError

from api.controllers.handle_order_status_transition.handlers.pos_terminal_registration.protocols import POSTerminalAdapterProtocol
from .exceptions import (
    POSTerminalAdapterValidationError,
    POSTerminalAdapterBadRequestError,
)
from .protocols import POSTerminalClientProtocol
from .schemas import POSTerminalRegistrationRequest


class POSTerminalAdapter(POSTerminalAdapterProtocol):
    def __init__(self, client: POSTerminalClientProtocol):
        self.__client = client

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
    ) -> str:
        try:
            POSTerminalRegistrationRequest(
                serial_number=serial_number,
                model=model,
                merchant_id=merchant_id,
                terminal_id=terminal_id,
                receiver_iin=receiver_iin,
                store_name=store_name,
                store_address=store_address,
                branch_name=branch_name,
                oked_code=oked_code,
                mcc_code=mcc_code,
                receiver_phone_number=receiver_phone_number,
                receiver_full_name=receiver_full_name,
                courier_full_name=courier_full_name,
                request_number_ref=request_number_ref,
                is_installment_enabled=is_installment_enabled,
            )
        except ValidationError as e:
            raise POSTerminalAdapterValidationError(e) from e

        try:
            response = await self.__client.registrate_pos_terminal(
                serial_number=serial_number,
                model=model,
                merchant_id=merchant_id,
                terminal_id=terminal_id,
                receiver_iin=receiver_iin,
                store_name=store_name,
                store_address=store_address,
                branch_name=branch_name,
                oked_code=oked_code,
                mcc_code=mcc_code,
                receiver_phone_number=receiver_phone_number,
                receiver_full_name=receiver_full_name,
                courier_full_name=courier_full_name,
                request_number_ref=request_number_ref,
                is_installment_enabled=is_installment_enabled,
            )
        except (HTTPStatusError, RequestError) as e:
            raise POSTerminalAdapterBadRequestError("can not registrate pos terminal, bad request") from e

        response_data = response.json()

        business_key = response_data.get('businessKey')

        return business_key
