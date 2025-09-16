from .. import models
from .. import schemas


async def history_get_list(pagination_params, **kwargs):
    model_type = kwargs.get('model_type')
    if model_type:
        kwargs['model_type'] = model_type.value
    history = await models.history_get_list(pagination_params, **kwargs)
    return history
