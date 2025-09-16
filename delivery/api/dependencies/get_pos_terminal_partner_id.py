from api.conf import conf

async def get_pos_terminal_partner_id() -> int:
    return conf.pos_terminal.partner_id
