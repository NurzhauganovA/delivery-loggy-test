from api.conf import conf

def get_freedom_bank_partner_id() -> int:
    return conf.freedom_bank.partner_id


def get_pos_terminal_partner_id() -> int:
    return conf.pos_terminal.partner_id
