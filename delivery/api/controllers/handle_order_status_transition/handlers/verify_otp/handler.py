from typing import Optional, Union

from pydantic import ValidationError
from tortoise.transactions import in_transaction

from api import models
from api.adapters.freedom_bank_otp.exceptions import BaseOTPError as FreedomBankOTPError
from api.adapters.pos_terminal_otp.exceptions import BaseOTPError as PosTerminalOTPError
from api.adapters.freedom_bank_otp.exceptions import OTPWrongOTPCode as FreedomBankWrongCodeError
from api.adapters.pos_terminal_otp.exceptions import OTPInvalidOTPCode as PosTerminalWrongCodeError
from api.controllers.handle_order_status_transition.handler_protocol import OrderStatusTransitionHandlerProtocol
from .exceptions import (
    VerifyOTPError,
    VerifyOTPValidationError,
    VerifyOTPPartnerNotFoundError,
    VerifyOTPWrongCodeError,
)
from .protocols import PosTerminalVerifyOTPProtocol, FreedomBankVerifyOTPProtocol
from .schema import VerifyOTPSchema

PartnerID = int

VerifyOTPAdapters = dict[PartnerID, Union[PosTerminalVerifyOTPProtocol, FreedomBankVerifyOTPProtocol]]


class VerifyOTPHandler(OrderStatusTransitionHandlerProtocol):
    def __init__(
        self,
        verify_otp_adapters: VerifyOTPAdapters,
    ):
        self.__verify_otp_adapters = verify_otp_adapters

    async def handle(
            self,
            order_obj: 'models.Order',
            status: 'models.Status',
            data: Optional[dict] = None,
    ):
        """Обработчик перевода заявки в статус verify_otp"""

        # Проверим корректность переданных данных в data
        if not data:
            raise VerifyOTPValidationError('data is required')

        try:
            payload = VerifyOTPSchema(**data)
        except ValidationError as e:
            raise VerifyOTPValidationError('invalid data provided') from e

        partner_id = order_obj.partner_id
        otp_code = payload.code
        code_sent_point = payload.code_sent_point

        # Получим ОТП сервис партнера и вызовем его
        if adapter := self.__verify_otp_adapters.get(partner_id):
            try:
                if isinstance(adapter, FreedomBankVerifyOTPProtocol):
                    await adapter.verify(
                        partner_order_id=order_obj.partner_order_id,
                        otp_code=otp_code,
                    )

                if isinstance(adapter, PosTerminalVerifyOTPProtocol):
                    product = await order_obj.product
                    business_key = product.attributes.get('business_key')
                    courier = await order_obj.courier
                    user = await courier.user
                    await adapter.verify(
                        phone_number=order_obj.receiver_phone_number,
                        business_key=business_key,
                        otp_code=otp_code,
                        courier_full_name=user.fullname,
                    )
            except (FreedomBankWrongCodeError, PosTerminalWrongCodeError) as e:
                raise VerifyOTPWrongCodeError('wrong code') from e
            except (FreedomBankOTPError, PosTerminalOTPError) as e:
                raise VerifyOTPError('error during verify otp') from e

        else:
            raise VerifyOTPPartnerNotFoundError(f'No OTP service for partner, partner_id: {partner_id}')

        # Сохраним гео локацию, если передали координаты
        geolocation = await order_obj.geolocation
        if geolocation and code_sent_point:
            geolocation = await order_obj.geolocation.select_for_update()
            geolocation.code_sent_point = code_sent_point.to_tuple()
            await geolocation.save()

        # TODO: Пока тут делаем переход на следующий статус, пока не ясно, переходить на текущий статус или на следующий.
        next_status = await models.Status.get(code='photo_capturing')
        order_time = await order_obj.localtime
        order_obj.current_status = next_status
        async with in_transaction():
            await models.OrderStatuses.create(order=order_obj, status=next_status, created_at=order_time)
            await order_obj.save()
