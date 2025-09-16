import fastapi

from api import auth, schemas
from api.schemas import pagination
from api.schemas.mobile.get_history import GetHistoryResponse, HistoryFilterParams
from api.views import mobile as mobile_views

router = fastapi.APIRouter()


@router.get(
    '/history',
    summary='Get list of history for mobile',
    response_description='List of history records',
    response_model=pagination.Page[GetHistoryResponse],
)
async def get_history_list(
    filter_params: HistoryFilterParams = fastapi.Depends(HistoryFilterParams),
    pagination_params: pagination.Params = fastapi.Depends(pagination.Params),
    _: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    return await mobile_views.get_history_list(pagination_params, filter_params)
