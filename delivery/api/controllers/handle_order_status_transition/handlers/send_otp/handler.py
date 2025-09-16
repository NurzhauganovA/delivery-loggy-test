from typing import Optional, Union

from pydantic import ValidationError

from api import models
from api.adapters.freedom_bank_otp.exceptions import BaseOTPError as FreedomBankOTPError
from api.adapters.pos_terminal_otp.exceptions import BaseOTPError as PosTerminalOTPError
from api.controllers.handle_order_status_transition.handler_protocol import OrderStatusTransitionHandlerProtocol
from .exceptions import (
    SendOTPValidationError,
    SendOTPError,
    SendOTPPartnerNotFoundError,
)
from .protocols import (
    PosTerminalSendOTPProtocol,
    FreedomBankSendOTPProtocol,
)
from .schema import Coordinates

PartnerID = int

SendOTPAdapters = dict[PartnerID, Union[PosTerminalSendOTPProtocol, FreedomBankSendOTPProtocol]]


class SendOTPHandler(OrderStatusTransitionHandlerProtocol):
    def __init__(
        self,
        send_otp_adapters: SendOTPAdapters,
    ):
        self.__send_otp_adapters = send_otp_adapters

    async def handle(
            self,
            order_obj: 'models.Order',
            status: 'models.Status',
            data: Optional[dict] = None,
    ):
        """Обработчик перевода заявки в статус send_otp"""

        # Проверим корректность переданных данных в data
        if data:
            try:
                Coordinates(**data)
            except ValidationError as e:
                raise SendOTPValidationError('invalid coordinates provided') from e

        partner_id = order_obj.partner_id

        # Получим ОТП сервис партнера и вызовем его
        if adapter := self.__send_otp_adapters.get(partner_id):
            try:
                if isinstance(adapter, PosTerminalSendOTPProtocol):
                    product = await order_obj.product
                    business_key = product.attributes.get('business_key')
                    await adapter.send(
                        phone_number=order_obj.receiver_phone_number,
                        business_key=business_key,
                    )

                if isinstance(adapter, FreedomBankSendOTPProtocol):
                    await adapter.send(
                        partner_order_id=order_obj.partner_order_id,
                )
            except (FreedomBankOTPError, PosTerminalOTPError) as e:
                raise SendOTPError(f'error during send OTP: {e}') from e

        else:
            raise SendOTPPartnerNotFoundError(f'No OTP service for partner, partner_id: {partner_id}')

        order_time = await order_obj.localtime

        # Сохраним гео локацию, если передали координаты
        geolocation = await order_obj.geolocation
        if not geolocation and order_obj.courier_id:
            location = Coordinates(**data).to_tuple() if data else None
            await models.OrderGeolocation.create(
                order_id=order_obj.id,
                at_client_point=location,
                courier_id=order_obj.courier_id,
                created_at=order_time,
            )

        # TODO: Пока для обратной совместимости не меняем статус
        # Сохраним изменение статуса у заявки
        # order_obj.current_status_id = status.id
        # await order_obj.save()
