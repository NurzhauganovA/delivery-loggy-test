from pydantic import ValidationError

from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist

from api import models
from api import enums

from api.schemas.history import HistoryCreate
from api.controllers.update_order_delivery_point import(
    schemas,
    exceptions,
)

from api.utils.area import polygon


class UpdateOrderDeliveryPoint:

    allowed_roles = (
        enums.ProfileType.SERVICE_MANAGER,
        enums.ProfileType.COURIER,
        enums.ProfileType.SUPERVISOR,
    )
    delivery_status = {
        'status': enums.OrderDeliveryStatusQuery.ADDRESS_CHANGED.value,
        'datetime': None,
        'reason': None,
        'comment': None,
    }
    role_available_statuses = {
        enums.ProfileType.COURIER: (
            enums.StatusSlug.COURIER_ASSIGNED.value,
            enums.StatusSlug.ACCEPTED_BY_COURIER.value,
        ),
        enums.ProfileType.SUPERVISOR: (
            enums.StatusSlug.COURIER_ASSIGNED.value,
            enums.StatusSlug.ACCEPTED_BY_COURIER.value,
            enums.StatusSlug.READY_TO_SEND.value,
            enums.StatusSlug.ACCEPTED_BY_COURIER_SERVICE.value,
        ),
        enums.ProfileType.SERVICE_MANAGER: (
            enums.StatusSlug.COURIER_ASSIGNED.value,
            enums.StatusSlug.ACCEPTED_BY_COURIER.value,
            enums.StatusSlug.READY_TO_SEND.value,
            enums.StatusSlug.ACCEPTED_BY_COURIER_SERVICE.value,
        ),
    }

    async def __data_valid(self, data: dict) -> bool:
        """
        Проверка тела запроса на валидность

        Args:
            data: данные полученные при запросе

        Returns:
            Статус проверки
        """

        try:
            schemas.ValidDeliveryPoint(**data)
            return True
        except ValidationError:
            return False

    async def __need_update_courier(
            self, user_role: str, area: models.Area, lat: float, lon: float
        ) -> bool:
        """
        Проверка на требование обновление курьера:
            Роль на супервизора
            На наличие зон доставки
            Содержание точки адреса в зоне доставке курьера

        Args:
            user_role: роль пользователя в системе
            order_obj: объект заказа из таблицы
            lat: долгота
            lon: широта
        Returns:
            Статус проверки
        """

        if user_role in (enums.ProfileType.SUPERVISOR, enums.ProfileType.SERVICE_MANAGER):
            return True
        if not area:
            return True

        area_polygon = []
        area_scopes = area.scope
        for area_scope in area_scopes:
            area_polygon.append(tuple(area_scope.values()))

        return not await polygon.contains_point(lat, lon, area_polygon)

    async def __available_update_order_status(self, user_role: str, order_status: str) -> bool:
        """
        Проверка на статусы, доступные к изменениям
        В зависимости от роли

        Args:
            user_role: роль пользователя в системе
            order_status: текущий статус заказа

        Returns:
            Статус проверки
        """

        available_statuses = self.role_available_statuses.get(user_role)
        if not available_statuses:
            return False
        return order_status in available_statuses

    async def __restore_order_statuses(self, order_obj: models.Order) -> models.Status:
        """
        Сброс статусов заказа до начальной точки отправки
        "Новая заявка"

        Args:
            order_obj: объект записи заказа

        Returns:
            Объект нового статуса
        """

        await models.OrderStatuses.filter(order_id=order_obj.id).delete()
        order_time = await order_obj.localtime
        status = await models.Status.get(slug=enums.StatusSlug.NEW.value)
        # Обнуляем все статусы до нового статуса
        await models.OrderStatuses.create(
            order=order_obj, status=status, created_at=order_time,
        )
        return status

    async def init(
            self, user_id: int,
            order_id: int,
            user_role: str,
            data: dict,
            default_filter_args: list = [],
        ) -> None:
        """
        Инициализация обновления точки доставки заказа

        Args:
            user_id: идентификатор пользователя
            order_id: идентификатор заказа
            user_role: роль пользователя в системе
            data: данные полученные при запросе
            {
                "delivery_point": {
                    "latitude": 12.345678,
                    "longitude": 12.345678,
                    "address": "Улица Карабаса, Дом Барабаса 7"
                },
                "comment": "Полнейшее отсутствие желания ехать к этому неадеквату"
            }
            default_filter_args: стандартные аргументы фильтрации по ролям
        Returns:
            None
        """

        if user_role not in self.allowed_roles:
            raise exceptions.RoleUnavailable('allowed only for couriers and supervisor')

        if not await self.__data_valid(data):
            raise exceptions.InvalidBody('invalid body')

        try:
            order_obj = await models.Order.filter(*default_filter_args).get(
                id=order_id
            ).prefetch_related(
                'area'
            ).prefetch_related(
                'delivery_point'
            ).prefetch_related('status_set')
        except DoesNotExist:
            raise DoesNotExist(f'Order with given ID: {order_id} was not found')

        current_status = await order_obj.current_status.first()

        if not await self.__available_update_order_status(user_role, current_status.slug):
            raise exceptions.CantUpdateOrderStatus('update unavailable')

        comment = data.get('comment')
        if comment:
            order_obj.comment = comment

        delivery_point = data['delivery_point']
        lat = delivery_point['latitude']
        lon = delivery_point['longitude']
        address = delivery_point['address']

        delivery_point = await order_obj.delivery_point.first()

        update_dict = {
            'change_type': enums.OrderDeliveryStatusQuery.ADDRESS_CHANGED.value,
            'change_reson': enums.OrderDeliveryStatusQuery.ADDRESS_CHANGED.value,
            'comment': comment,
            'delivery_point': {
                'address': address,
                'latitude': lat,
                'longitude': lon,
            },
            'old_delivery_point': {
                'id': delivery_point.id,
                'address': delivery_point.address,
            }
        }

        delivery_point.latitude = lat
        delivery_point.longitude = lon
        delivery_point.address = address

        area = await order_obj.area.first() if order_obj.area else None

        if await self.__need_update_courier(user_role, area, lat, lon):
            order_obj.courier_id = None
            order_obj.delivery_status = self.delivery_status
            order_obj.current_status = await self.__restore_order_statuses(order_obj)

        async with in_transaction():
            await delivery_point.save()
            await order_obj.save()

        created_at = await order_obj.localtime
        await models.history_create(
            HistoryCreate(
                initiator_type=enums.InitiatorType.USER,
                initiator_id=user_id,
                initiator_role=user_role,
                model_type=enums.HistoryModelName.ORDER,
                model_id=order_id,
                request_method=enums.RequestMethods.PUT,
                action_data=update_dict,
                created_at=created_at,
            )
        )
