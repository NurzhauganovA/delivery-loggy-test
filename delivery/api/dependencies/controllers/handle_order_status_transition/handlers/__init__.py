from .new import get_new_handler
from .card_returned_to_bank import get_card_returned_to_bank_handler
from .pos_terminal_registration import get_pos_terminal_registration_handler
from .send_otp import get_send_otp_handler
from .verify_otp import get_verify_otp_handler
from .transfer_to_sdek import get_transfer_to_cdek_handler


__all__ = [
    'get_new_handler',
    'get_card_returned_to_bank_handler',
    'get_pos_terminal_registration_handler',
    'get_send_otp_handler',
    'get_verify_otp_handler',
    'get_transfer_to_cdek_handler',
]
