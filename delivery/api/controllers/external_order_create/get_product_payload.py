from typing import Optional, Union

from api.enums import ProductType
from api.schemas.order_payload import (
    CardPayload,
    POSTerminalPayload,
    GroupOfCardsPayload,
)


def get_product_payload(
        product_type: str,
        payload: Optional[Union[CardPayload, POSTerminalPayload]],
):
    product_payload = None

    if product_type == ProductType.CARD:
        product_payload = CardPayload.parse_obj(payload)

    if product_type == ProductType.POS_TERMINAL:
        product_payload = POSTerminalPayload.parse_obj(payload)

    if product_type == ProductType.GROUP_OF_CARDS:
        product_payload = GroupOfCardsPayload.parse_obj(payload)

    return product_payload
