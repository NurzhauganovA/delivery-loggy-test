import fastapi
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from api.auth import get_current_user
from api.dependencies import OrderDefaultFilterV2
from api.views import get_order
from api.schemas import UserCurrent
from api.schemas.crm import GetOrderResponse

router = fastapi.APIRouter()

@router.get(
    '/order/{order_id}',
    summary='Get order for CRM',
    response_model=GetOrderResponse,
    response_description='Get order for CRM',
)
async def get_order_crm(
    order_id: int,
    _: UserCurrent = fastapi.Security(get_current_user, scopes=['o:g']),
    default_filter_args: list = fastapi.Security(OrderDefaultFilterV2()),
):
    result = await get_order(
        order_id=order_id,
        default_filter_args=default_filter_args,
    )
    return JSONResponse(jsonable_encoder(result))
