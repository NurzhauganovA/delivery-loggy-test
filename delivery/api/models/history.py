import tortoise
from fastapi_pagination.ext.tortoise import paginate

from .. import enums
from .. import models
from .. import schemas
from .. import utils
from ..modules.order_chain.infrastructure.db_table import OrderChainHistory
from ..modules.shipment_point.infrastructure.db_table import PartnerShipmentPointHistory

fields = tortoise.fields


class HistoryCreationError(Exception):
    """Raises when history creation drops error."""


class History(tortoise.Model):
    initiator_id = fields.IntField(null=True)
    initiator_type = fields.CharEnumField(
        **enums.InitiatorType.to_kwargs(
            default=enums.InitiatorType.USER
        )
    )
    request_method = fields.CharEnumField(**enums.RequestMethods.to_kwargs())
    model_type = fields.CharField(max_length=50)
    model_id = fields.IntField(null=True)
    action_type = fields.CharEnumField(**enums.ActionType.to_kwargs(null=True))
    action_data = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    initiator_role = fields.CharEnumField(**enums.ProfileType.to_kwargs(null=True))

    class Meta:
        table = 'history'


@utils.as_dict(from_model=True)
async def history_create(schema: schemas.HistoryCreate):
    try:
        if schema.model_type == enums.HistoryModelName.ORDER_CHAIN.value:
            return await OrderChainHistory.create(**schema.dict(exclude_unset=True))

        if schema.model_type == enums.HistoryModelName.PARTNER_SHIPMENT_POINTS.value:
            return await PartnerShipmentPointHistory.create(**schema.dict(exclude_unset=True))

        return await History.create(**schema.dict(exclude_unset=True))
    except tortoise.exceptions.IntegrityError as e:
        raise HistoryCreationError(e)

async def serialize_initiator_info(queryset):
    for history in queryset:
        if history.initiator_type in [
            enums.InitiatorType.USER.value, enums.InitiatorType.IMPORT.value
        ]:
            try:
                initiator = await models.user_get(with_history=False,
                                                  id=history.initiator_id)
                profiles = await models.get_all_user_profiles(initiator['id'])
                profile_types = ([history.initiator_role, ] if history.initiator_role
                                 else [value['type'] for value in profiles])
                history.initiator = {
                    'id': initiator['id'],
                    'profile_types': profile_types,
                    'first_name': initiator['first_name'],
                    'last_name': initiator['last_name'],
                    'middle_name': initiator['middle_name'],
                }
            except models.UserNotFound:
                history.initiator = {}
        else:
            initiator = await models.partner_get(
                partner_id=history.initiator_id, with_info=False
            )
            history.initiator = {
                'id': initiator.get('id', None),
                'name_en': initiator.get('name_en', None),
                'name_kk': initiator.get('name_kk', None),
                'name_ru': initiator.get('name_ru', None),
                'name_zh': initiator.get('name_zh', None),
            }

async def history_get_list(pagination_params=None, **kwargs):
    if kwargs.get('model_type', None) == enums.HistoryModelName.ORDER_CHAIN.value:
        qs = OrderChainHistory.filter(**kwargs).order_by('-created_at')
    elif kwargs.get('model_type', None) == enums.HistoryModelName.PARTNER_SHIPMENT_POINTS.value:
        qs = PartnerShipmentPointHistory.filter(**kwargs).order_by('-created_at')
    else:
        qs = History.filter(**kwargs).order_by('-created_at')
    if pagination_params:
        result = await paginate(qs, params=pagination_params)
        queryset = result.items
    else:
        result = [schemas.HistoryGet.from_orm(item) for item in await qs]
        queryset = result

    await serialize_initiator_info(queryset)

    return result
