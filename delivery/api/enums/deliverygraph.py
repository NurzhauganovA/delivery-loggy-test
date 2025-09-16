from .descriptor import Descriptor


class DeliveryGraphIcons(Descriptor):
    ORDER_NEW = 'order_new'
    ORDER_ACCEPTED = 'order_accepted'
    SERVICE_CENTER = 'service_center'
    AT_CLIENT = 'at_client'
    POST_CONTROL = 'post_control'
    COURIER_APPOINTED = 'courier_appointed'
    COURIER_ACCEPTED = 'courier_accepted'
    OTW_DELIVERY_POINT = 'otw_delivery_point'
    ON_DELIVERY_POINT = 'on_delivery_point'
    ORDER_DELIVERED = 'order_delivered'
    BEING_FINALIZED = 'post_control_declined'


class DeliverygraphSlugs(Descriptor):
    PODGOTOVKA_OTP_POSLEDCONTROL = 'Podgotovka + otp + Posledkontrol'
    OTP_SCAN_POST = 'otp-scan-posledkontrol'
    PICKUP_OTP_SCAN_POST = 'Pickup with otp + scan + postcontrol'
    OTP_SCAN = 'otp + scan'
