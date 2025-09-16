from typing import Optional

from httpx import (
    AsyncClient,
    HTTPStatusError,
    RequestError,
)

from api.adapters.pos_terminal.protocols import POSTerminalClientProtocol
from api.logging_module import logger


class POSTerminalClient(POSTerminalClientProtocol):
    def __init__(self, base_url: str, authorization: str):
        self.__client = AsyncClient(
            base_url=base_url,
            headers={"Authorization": authorization},
        )

    async def aclose(self):
        await self.__client.aclose()

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
            sum: Optional[float],
    ):
        body = {
            "serialNo": serial_number,
            "manufacturer": model,
            "mid": merchant_id,
            "tid": terminal_id,
            "iinBin": receiver_iin,
            "deliveryPointName": store_name,
            "deliveryPointAddress": store_address,
            "branchCode": branch_name,
            "oked": oked_code,
            "mccCode": mcc_code,
            "phoneNumber": receiver_phone_number,
            "clientFio": receiver_full_name,
            "isCl": is_installment_enabled,
            "inventoryNumber": inventory_number,
            "sum": sum,
        }

        if request_number_ref:
            body["requestNumRef"] = request_number_ref

        try:
            response = await self.__client.post(
                url="/process/startBts",
                json=body,
                params={
                    "manager": courier_full_name
                }
            )
        except RequestError as e:
            logger.error(e)
            raise e

        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            logger.bind(
                status_code=response.status_code,
                method="POST",
                url=str(response.url),
                body=body,
                response=response.text,
            ).error(e)
            raise e

        return response