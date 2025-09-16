import pytest
from httpx import (
    Response,
    Request,
    HTTPStatusError,
)

from api.adapters.pos_terminal_otp import (
    PosTerminalOTPAdapter,
    PosTerminalOTPClientProtocol,
)


@pytest.fixture
def client() -> PosTerminalOTPClientProtocol:
    class MockClient(PosTerminalOTPClientProtocol):
        async def send(self, business_key: str, phone_number: str) -> Response:
            if phone_number == '+77000000001' and business_key:
                return Response(
                    status_code=400,
                    json='FAILURE',
                    request=Request('POST', 'https://example.com/test'),
                )
            elif phone_number == '+77000000002' and business_key:
                request = Request('POST', 'https://example.com/test')
                response = Response(
                    status_code=500,
                    json='Internal Server Error',
                    request=request,
                )
                raise HTTPStatusError(message='', response=response, request=request)
            else:
                return Response(
                    status_code=202,
                    request=Request('POST', 'https://example.com/test'),
                )

        async def verify(
            self,
            business_key: str,
            phone_number: str,
            otp_code: str,
            courier_full_name: str,
         ) -> Response:
            if otp_code == '1111':
                return Response(
                    status_code=200,
                    json='SUCCESS',
                    request=Request('POST', 'https://example.com/test'),
                )
            elif otp_code == '2222':
                request = Request('POST', 'https://example.com/test')
                response = Response(
                    status_code=500,
                    json='Internal Server Error',
                    request=request,
                )
                raise HTTPStatusError(message='', response=response, request=request)
            elif otp_code == '3333':
                return Response(
                    status_code=200,
                    json='FAILURE',
                    request=Request('POST', 'https://example.com/test'),
                )
            elif otp_code == '4444':
                return Response(
                    status_code=200,
                    json='NOT_FOUND',
                    request=Request('POST', 'https://example.com/test'),
                )
            else:
                return Response(
                    status_code=200,
                    json='SUCCESS',
                    request=Request('POST', 'https://example.com/test'),
                )

    return MockClient()


@pytest.fixture
def adapter(
        client: PosTerminalOTPClientProtocol,
) -> PosTerminalOTPAdapter:
    return PosTerminalOTPAdapter(
        client=client,
    )
