import pytest
from httpx import (
    Response,
    Request, HTTPStatusError,
)

from api.adapters.freedom_bank_otp import (
    FreedomBankOTPAdapter,
    FreedomBankOTPProtocol,
)


@pytest.fixture
def client() -> FreedomBankOTPProtocol:
    class MockClient(FreedomBankOTPProtocol):
        async def send(self, request_id: str, phone_number: str) -> Response:
            if phone_number == "77000000001" and request_id:
                return Response(
                    status_code=400,
                    json={
                        "timestamp": "2025-04-25T09:22:14.959+00:00",
                        "status": 400,
                        "error": "Bad Request",
                        "path": "/otp/send-international"
                    },
                    request=Request("POST", "https://example.com/test"),
                )
            elif phone_number == "77000000002" and request_id:
                request = Request("POST", "https://example.com/test")
                response = Response(
                    status_code=500,
                    json={
                        "timestamp": "2025-04-25T09:22:47.952+00:00",
                        "status": 500,
                        "error": "Internal Server Error",
                        "path": "/otp/send-international"
                    },
                    request=request,
                )
                raise HTTPStatusError(message="", response=response, request=request)
            else:
                return Response(
                    status_code=202,
                    request=Request("POST", "https://example.com/test"),
                )

        async def verify(self, request_id: str, phone_number: str, otp_code: str) -> Response:
            if otp_code == "1111":
                return Response(
                    status_code=200,
                    json={
                        "success": True,
                        "errorCode": None,
                        "errorMessage": None,
                        "payload": "NOT_FOUND"
                    },
                    request=Request("POST", "https://example.com/test"),
                )
            elif otp_code == "2222":
                request = Request("POST", "https://example.com/test")
                response = Response(
                    status_code=500,
                    json={
                        "timestamp": "2025-04-25T09:22:47.952+00:00",
                        "status": 500,
                        "error": "Internal Server Error",
                        "path": "/otp/verify-international"
                    },
                    request=request,
                )
                raise HTTPStatusError(message="", response=response, request=request)
            elif otp_code == "3333":
                return Response(
                    status_code=200,
                    json={
                        "success": True,
                        "errorCode": None,
                        "errorMessage": None,
                        "payload": "FAILURE"
                    },
                    request=Request("POST", "https://example.com/test"),
                )
            else:
                return Response(
                    status_code=200,
                    json={
                        "success": True,
                        "errorCode": None,
                        "errorMessage": None,
                        "payload": "SUCCESS"
                    },
                    request=Request("POST", "https://example.com/test"),
                )

    return MockClient()


@pytest.fixture
def adapter(
        client: FreedomBankOTPProtocol,
) -> FreedomBankOTPAdapter:
    return FreedomBankOTPAdapter(
        client=client,
    )
