from api.controllers.handle_order_status_transition.handlers import NewHandler

__singleton: NewHandler | None = None


def get_new_handler() -> NewHandler:
    global __singleton
    if __singleton is None:
        __singleton = NewHandler()

    return __singleton
