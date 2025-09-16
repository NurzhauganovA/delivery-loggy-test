from .infrastructure.repository import *
from .schemas import (
    CallRequestCreateSchema,
)
from ...common.action_base import BaseAction
from ...services.sms.notification import send_call_request


class CallRequestActions(BaseAction):
    def __init__(self, current_user=None):
        self.user = current_user
        self.repo = CallRequestRepository()
        self.contact_repo = CallRequestContactRepository()

    async def create(
        self, call_request: CallRequestCreateSchema,
    ) -> None:
        await self.repo.create(call_request)
        for phone, email in await self.contact_repo.get_contacts():
            await send_call_request(phone=phone, email=email, potential_customer=call_request.phone)
