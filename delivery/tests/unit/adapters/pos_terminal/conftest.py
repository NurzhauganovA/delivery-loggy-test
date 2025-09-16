from typing import Optional

import pytest
from httpx import (
    Response,
    Request,
    HTTPStatusError,
)

from api.adapters.pos_terminal import POSTerminalAdapter
from api.adapters.pos_terminal.protocols import POSTerminalClientProtocol


@pytest.fixture
def client() -> POSTerminalClientProtocol:

    class MockClient:
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
                sum: Optional[float]
        ) -> Response | HTTPStatusError:
            if serial_number == "222":
                request = Request("POST", "https://example.com/test")
                response = Response(
                    status_code=500,
                    request=request,
                )
                raise HTTPStatusError(message="", response=response, request=request)

            return Response(
                status_code=200,
                request=Request("POST", "http://example.com/test"),
                json={
                    "id": "3bd7f704-3f78-11f0-8fd1-fa6a92be66cf",
                    "definitionId": "OverdraftTMSProcess",
                    "businessKey": "OVERDRAFT-TMS25-02263",
                    "caseInstanceId": None,
                    "taskId": None,
                    "tenantId": None,
                    "ended": False,
                    "suspended": False
                }
            )

    return MockClient()


@pytest.fixture
def adapter(
        client: POSTerminalClientProtocol,
) -> POSTerminalAdapter:
    return POSTerminalAdapter(
        client=client,
    )
