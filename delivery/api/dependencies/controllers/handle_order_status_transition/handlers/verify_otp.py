from fastapi import Depends

from api.controllers.handle_order_status_transition.handlers import VerifyOTPHandler
from api.controllers.handle_order_status_transition.handlers.verify_otp.handler import VerifyOTPAdapters
from api.controllers.handle_order_status_transition.handlers.verify_otp.protocols import (
    FreedomBankVerifyOTPProtocol,
    PosTerminalVerifyOTPProtocol,
)
from api.dependencies.adapters.fredom_bank_otp import get_freedom_bank_otp_adapter
from api.dependencies.adapters.pos_terminal_otp import get_pos_terminal_otp_adapter
from api.dependencies.partners_ids import (
    get_freedom_bank_partner_id,
    get_pos_terminal_partner_id,
)

__singleton: VerifyOTPHandler | None = None


def __get_adapters(
    freedom_bank_partner_id: int = Depends(get_freedom_bank_partner_id),
    freedom_bank_otp_adapter: FreedomBankVerifyOTPProtocol = Depends(get_freedom_bank_otp_adapter),
    pos_terminal_partner_id: int = Depends(get_pos_terminal_partner_id),
    pos_terminal_otp_adapter: PosTerminalVerifyOTPProtocol = Depends(get_pos_terminal_otp_adapter),
) -> VerifyOTPAdapters:
    return {
        freedom_bank_partner_id: freedom_bank_otp_adapter,
        pos_terminal_partner_id: pos_terminal_otp_adapter,
    }


def get_verify_otp_handler(
        verify_otp_adapters: VerifyOTPAdapters = Depends(__get_adapters),
) -> VerifyOTPHandler:
    global __singleton
    if __singleton is None:
        __singleton = VerifyOTPHandler(
            verify_otp_adapters=verify_otp_adapters
        )

    return __singleton
