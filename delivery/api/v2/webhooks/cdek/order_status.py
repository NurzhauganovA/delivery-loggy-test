import fastapi
from fastapi import Depends

from api.controllers.webhooks.cdek import handle_order_status
from api.dependencies.webhooks.cdek import get_api_key
from api.schemas.webhooks.cdek import OrderStatusRequest

router = fastapi.APIRouter()


@router.post(
    '/order-status',
    summary='Webhook order status',
)
async def webhook_cdek_order_status(
    body: OrderStatusRequest,
    api_key: str,
    valid_api_key = Depends(get_api_key)
):
    if api_key != valid_api_key:
        return fastapi.responses.Response(status_code=403)

    await handle_order_status(request=body)
    return fastapi.responses.Response(status_code=200)
