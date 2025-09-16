from api import models
from .exceptions import ExternalOrderCreateDuplicateError


async def check_duplicate_partner_order(partner_order_id: str, partner_id: int) -> None:
    duplicate_order = await models.Order.filter(
        partner_order_id=partner_order_id,
        partner_id=partner_id
    ).first().values('id')

    if duplicate_order:
        raise ExternalOrderCreateDuplicateError(f"order already exists")
