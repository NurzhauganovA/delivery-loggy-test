from api.modules.partner_settings.infrastructure.repository import PartnerSettingRepository
from .schemas import (
    PartnerSettingGet,
    PartnerSettingUpdate
)
from typing import Union

from ...common.action_base import BaseAction
from ...enums import InitiatorType, RequestMethods, HistoryModelName
from ...models import history_create
from ...schemas import HistoryCreate


class PartnerSettingActions(BaseAction):
    def __init__(self, current_user = None):
        self.user = current_user
        self.repo = PartnerSettingRepository()

    async def partner_setting_update(
        self,
        partner_id: int,
        default_filter_args,
        update: PartnerSettingUpdate,
    ) -> None:
        # place for business logic
        settings_fetched = await self.repo.partial_update(
            partner_id=partner_id,
            update_schema=update,
            default_filter_args=default_filter_args,
        )

        await history_create(
            HistoryCreate(
                initiator_type=InitiatorType.USER,
                initiator_id=self.user.id,
                initiator_role=self.user.profile['profile_type'],
                model_type=HistoryModelName.PARTNER_SETTINGS,
                model_id=settings_fetched.id,
                request_method=RequestMethods.PATCH,
                action_data=update.dict()
            )
        )

        return settings_fetched

    async def partner_setting_get(
        self,
        partner_id: int,
        default_filter_args = None,
    ) -> Union[PartnerSettingGet, dict]:
        # place for business logic
        return await self.repo.get_by_id(
            partner_id=partner_id,
            default_filter_args=default_filter_args,
        )

