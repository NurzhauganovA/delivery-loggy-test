from fastapi import Depends

from api.controllers.handle_order_status_transition.handlers import SendOTPHandler
from api.controllers.handle_order_status_transition.handlers.send_otp.handler import SendOTPAdapters
from api.controllers.handle_order_status_transition.handlers.send_otp.protocols import (
    FreedomBankSendOTPProtocol,
    PosTerminalSendOTPProtocol,
)
from api.dependencies.adapters.fredom_bank_otp import get_freedom_bank_otp_adapter
from api.dependencies.adapters.pos_terminal_otp import get_pos_terminal_otp_adapter
from api.dependencies.partners_ids import (
    get_freedom_bank_partner_id,
    get_pos_terminal_partner_id,
)

__singleton: SendOTPHandler | None = None


def __get_adapters(
    freedom_bank_partner_id: int = Depends(get_freedom_bank_partner_id),
    freedom_bank_otp_adapter: FreedomBankSendOTPProtocol = Depends(get_freedom_bank_otp_adapter),
    pos_terminal_partner_id: int = Depends(get_pos_terminal_partner_id),
    pos_terminal_otp_adapter: PosTerminalSendOTPProtocol = Depends(get_pos_terminal_otp_adapter),
) -> SendOTPAdapters:
    return {
        freedom_bank_partner_id: freedom_bank_otp_adapter,
        pos_terminal_partner_id: pos_terminal_otp_adapter,
    }


def get_send_otp_handler(
        send_otp_adapters: SendOTPAdapters = Depends(__get_adapters),
) -> SendOTPHandler:
    global __singleton
    if __singleton is None:
        __singleton = SendOTPHandler(
            send_otp_adapters=send_otp_adapters
        )

    return __singleton
