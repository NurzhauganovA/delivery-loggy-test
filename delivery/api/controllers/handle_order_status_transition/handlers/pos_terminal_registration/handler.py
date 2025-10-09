from typing import Optional

from pydantic import ValidationError
from tortoise.exceptions import DoesNotExist

from api import models, enums
from api.adapters.pos_terminal.exceptions import BasePOSTerminalAdapterError
from api.controllers.handle_order_status_transition.handler_protocol import OrderStatusTransitionHandlerProtocol
from api.domain.products.pos_terminal import RegistrationStatus
from api.models.publisher import call_task
from .exceptions import (
    POSTerminalRegistrationHandlerValidationError,
    POSTerminalRegistrationHandlerIntegrationError,
    NotAllowPOSTerminalRegistration,
)
from .protocols import POSTerminalAdapterProtocol
from .schema import POSTerminalRegistrationData


class POSTerminalRegistrationHandler(OrderStatusTransitionHandlerProtocol):
    def __init__(self, adapter: POSTerminalAdapterProtocol):
        self.__adapter = adapter

    async def handle(
            self,
            order_obj: 'models.Order',
            status: 'models.Status',
            data: Optional[dict] = None,
    ):
        """Обработчик перевода заявки в статус pos_terminal_registration"""

        # Проверим корректность переданных данных в data
        if not data:
            raise POSTerminalRegistrationHandlerValidationError('data is required')

        try:
            pos_terminal_registration_data = POSTerminalRegistrationData(**data)
        except ValidationError as e:
            raise POSTerminalRegistrationHandlerValidationError(e) from e

        # Получим продукт у заявки
        try:
            product_obj = await models.Product.get(order_id=order_obj.id)
        except DoesNotExist:
            raise DoesNotExist(f'product with given order_id: {order_obj.id} was not found')

        # Проверим что продукт типа pos_terminal
        if product_obj.type != enums.ProductType.POS_TERMINAL:
            raise POSTerminalRegistrationHandlerValidationError(f'product has wrong type: {product_obj.type}, required type: {enums.ProductType.POS_TERMINAL}')

        # Проверим статус текущей регистрации
        current_registration_status = product_obj.attributes.get('registration_status')

        # Если нет статуса регистрации, вызываем регистрацию
        if current_registration_status is None:
            await self.__handle_first_registration(
                order_obj=order_obj,
                product_obj=product_obj,
                pos_terminal_registration_data=pos_terminal_registration_data,
            )

        # Если статус один из перечисленных ниже, то вызываем повторный опрос статуса
        if current_registration_status in (
                # RegistrationStatus.ERROR,  # TODO: Пока что этого статуса нет
                RegistrationStatus.CANCELED, # TODO: Вместо ERROR пока что CANCELED
                RegistrationStatus.TIMEOUT_ERROR,
        ):
            business_key = product_obj.attributes.get('business_key')
            await self.__start_requesting_status(business_key=business_key)

        # Если статус один из перечисленных ниже, то нельзя регистрировать pos терминал, возвращаем ошибку
        if current_registration_status in (
                RegistrationStatus.COMPLETED,
                RegistrationStatus.STARTED,
        ):
            raise NotAllowPOSTerminalRegistration(
                f'not allowed start registration, current registration_status: {current_registration_status}')


    async def __handle_first_registration(
            self,
            order_obj: 'models.Order',
            product_obj: 'models.Product',
            pos_terminal_registration_data: 'POSTerminalRegistrationData',
    ):

        product_obj.attributes['model'] = pos_terminal_registration_data.model
        product_obj.attributes['serial_number'] = pos_terminal_registration_data.serial_number

        product_attributes = product_obj.attributes

        courier_obj = await order_obj.courier
        user_obj = await courier_obj.user
        delivery_point_obj = await order_obj.delivery_point

        # Отправим запрос на регистрацию pos терминала
        try:
            business_key = await self.__adapter.registrate_pos_terminal(
                serial_number=pos_terminal_registration_data.serial_number,
                model=pos_terminal_registration_data.model,
                merchant_id=product_attributes.get('merchant_id'),
                terminal_id=product_attributes.get('terminal_id'),
                receiver_iin=order_obj.receiver_iin,
                store_name=product_attributes.get('store_name'),
                store_address=delivery_point_obj.address,
                branch_name=product_attributes.get('branch_name'),
                oked_code=product_attributes.get('oked_code'),
                mcc_code=product_attributes.get('mcc_code'),
                receiver_phone_number=order_obj.receiver_phone_number,
                receiver_full_name=order_obj.receiver_name,
                courier_full_name=user_obj.fullname,
                request_number_ref=product_attributes.get('request_number_ref'),
                is_installment_enabled=product_attributes.get('is_installment_enabled', False),
            )
        except BasePOSTerminalAdapterError as e:
            raise POSTerminalRegistrationHandlerIntegrationError(f'registrate pos terminal error: {e}') from e

        product_obj.attributes['business_key'] = business_key
        product_obj.attributes['registration_status'] = RegistrationStatus.STARTED

        await product_obj.save()

        # Вызовем асинхронную задачу опроса статуса регистрации pos терминала
        await self.__start_requesting_status(business_key=business_key)

    @staticmethod
    async def __start_requesting_status(business_key: str):
        await call_task(
            task_name='sync-pos-terminal-registration-status',
            data={
                "business_key": business_key,
            },
        )
