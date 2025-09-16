import fastapi

from api import responses
from api import schemas
from api.controllers.external_order_create import external_order_create

router = fastapi.APIRouter()


@router.post(
    '/external/order/create',
    summary='Create order',
    response_model=schemas.ExternalOrderCreateResponse,
    response_description='Created order',
    responses=responses.generate_responses([responses.APIResponseNotFound]),
)
async def create_external_order(
    order: schemas.ExternalOrderCreate,
    api_key: str
):
    order_id = await external_order_create(
        order=order,
        api_key=api_key
    )
    return schemas.ExternalOrderCreateResponse(order_id=order_id)

