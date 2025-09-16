import fastapi

from ... import auth
from ... import controllers
from ... import schemas


router = fastapi.APIRouter()


@router.get(
    '/history/list',
    summary='Get list of history',
    response_description='List of histories',
    response_model=schemas.Page[schemas.HistoryGet],
)
async def history_get_list(
    filter_params: schemas.HistoryFilterParams = fastapi.Depends(
        schemas.HistoryFilterParams,
    ),
    pagination_params: schemas.Params = fastapi.Depends(schemas.Params),
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    kwargs = {
        **filter_params.dict(exclude_unset=True, exclude_none=True)
    }
    return await controllers.history_get_list(pagination_params, **kwargs)
