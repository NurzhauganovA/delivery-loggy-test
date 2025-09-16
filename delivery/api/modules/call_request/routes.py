import fastapi

from ...auth import simple_auth
from .schemas import (
    CallRequestCreateSchema,
)

from .actions import CallRequestActions

router = fastapi.APIRouter()


@router.post(
    '/call-request',
    summary='Create call request',
    response_description='Call request created',
)
async def call_request_create(
    call_request: CallRequestCreateSchema,
    _: None = fastapi.Security(simple_auth),
):
    """Create call request with given payload."""

    actions = CallRequestActions()
    await actions.create(
        call_request=call_request,
    )

    return fastapi.responses.Response(status_code=201)
