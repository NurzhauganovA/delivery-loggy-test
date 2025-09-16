from api.controllers.handle_order_status_transition.handlers import CardReturnedToBankHandler

__singleton: CardReturnedToBankHandler | None = None


def get_card_returned_to_bank_handler() -> CardReturnedToBankHandler:
    global __singleton
    if __singleton is None:
        __singleton = CardReturnedToBankHandler()

    return __singleton
