from .descriptor import Descriptor


class MessageType(Descriptor):
    LOCATION = 'location'
    NEW_ORDER = 'new_order'
    ORDER_STATUS_UPDATE = 'order_status_update'
    SUCCESS = 'success'
    ERROR = 'error'
    REQUEST = 'request'
    COURIER_PROFILE_STATUS_UPDATE = 'courier_profile_status_update'
    POSTCONTROL = 'postcontrol'
    DELIVERY_STATUS_UPDATE = 'delivery_status_update'
