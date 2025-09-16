from .. import models
from .. import schemas


async def deliverygraph_default_get() -> list:
    return await models.deliverygraph_list_default()


async def deliverygraph_get(deliverygraph_id: int, **kwargs):
    return await models.deliverygraph_get(deliverygraph_id, **kwargs)


async def deliverygraph_get_list(partner_id: int) -> list:
    return await models.deliverygraph_get_list(partner_id=partner_id)


async def deliverygraph_create(
    deliverygraph: schemas.DeliveryGraphCreate,
    **kwargs,
):
    return await models.deliverygraph_create(deliverygraph, **kwargs)


async def deliverygraph_update(
        deliverygraph_id: int, update: schemas.DeliveryGraphUpdate,
        **kwargs,
):

    return await models.deliverygraph_update(
        deliverygraph_id, update, **kwargs,
    )


async def deliverygraph_delete(deliverygraph_id: int, **kwargs) -> None:
    await models.deliverygraph_delete(deliverygraph_id, **kwargs)
