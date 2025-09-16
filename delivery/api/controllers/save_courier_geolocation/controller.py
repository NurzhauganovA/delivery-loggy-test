import typing

from api import schemas, models, enums


async def save_courier_geolocation(
        courier: schemas.UserCurrent,
        data: schemas.SaveCourierGeolocation,
        default_filter_args: typing.List,
):
    order_obj = await models.Order.filter(*default_filter_args).get(id=data.order_id)
    order_time = await order_obj.localtime

    await models.history_create(
        schemas.HistoryCreate(
            initiator_type=enums.InitiatorType.USER,
            initiator_id=courier.id,
            initiator_role=courier.profile['profile_type'],
            model_type=enums.HistoryModelName.ORDER,
            model_id=order_obj.id,
            request_method=enums.RequestMethods.POST,
            action_data={
                'coordinates': {
                    'latitude': data.latitude,
                    'longitude': data.longitude
                },
            },
            created_at=order_time,
        )
    )
