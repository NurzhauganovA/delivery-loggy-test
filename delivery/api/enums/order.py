from . import descriptor


class OrderType(descriptor.Descriptor):
    URGENT = 'urgent'
    OPERATIVE = 'operative'
    PLANNED = 'planned'
    PICKUP = 'pickup'


class ProductType(descriptor.Descriptor):
    CARD = 'card'
    POS_TERMINAL = 'pos_terminal'
    GROUP_OF_CARDS = 'group_of_cards'


class CreatedType(descriptor.Descriptor):
    IMPORT = 'import'
    INTEGRATION = 'integration'
    SERVICE = 'service'


class OrderSearchType(descriptor.Descriptor):
    ID = 'id'
    IIN = 'inn'
    PHONE = 'phone'
    FULL_NAME = 'full_name'
    CARD_NUMBER = 'card_number'
    TRACK_NUMBER = 'track_number'


class OrderStatus(descriptor.Descriptor):
    NEW = 1
    COURIER_ASSIGNED = 2
    ACCEPTED_BY_COURIER = 3
    ON_THE_WAY = 4
    AT_THE_POINT = 5
    CONTACT_WITH_CUSTOMER = 6
    DELIVERED = 7
    SENT_FOR_PREPARATION = 8
    PREPARE_TO_SEND = 9
    READY_TO_SEND = 10
    AT_THE_CALL_POINT = 11
    POST_CONTROL = 12
    POST_CONTROL_BANK = 33
    REASSIGNMENT = 13
    ISSUED = 27
    READY_FOR_SHIPMENT = 28
    ENDED = 34


# Переезжаем на этот enum. Он смотрит в колонку code в таблице status
class OrderStatusCodes(descriptor.Descriptor):
    NEW = 'new'
    CARD_RETURNED_TO_BANK = 'card_returned_to_bank'
    POS_TERMINAL_REGISTRATION = 'pos_terminal_registration'
    SEND_OTP = 'send_otp'
    TRANSFER_TO_CDEK = 'transfer_to_cdek'


class StatusIcon(descriptor.Descriptor):
    NEW = 'new'
    COURIER_ASSIGNED = 'courier-assigned'
    ACCEPTED_BY_COURIER = 'accepted-by-courier'
    ON_THE_WAY = 'on-the-way'
    AT_THE_POINT = 'at-the-point'
    CONTACT_WITH_CUSTOMER = 'contact-with-customer'
    DELIVERED = 'delivered'
    SENT_FOR_PREPARATION = 'sent-for-preparation'
    PREPARE_TO_SEND = 'prepare-to-send'
    READY_TO_SEND = 'ready-to-send'
    AT_THE_CALL_POINT = 'at-the-call-point'
    PACKAGE_AT_COURIER = 'package-at-courier'
    POST_CONTROL = 'post-control'
    REASSIGNMENT = 'reassignment'
    DELIVERED_WITHOUT_POST_INSPECTION = 'delivered-without-post-inspection'
    POST_CONTROL_REVISION = 'post-control-revision'


class StatusSlug(descriptor.Descriptor):
    NEW = 'novaia-zaiavka'
    TRANSFER_TO_CDEK = 'transfer_to_cdek'
    COURIER_ASSIGNED = 'kurer-naznachen'
    ACCEPTED_BY_COURIER = 'priniato-kurerom-v-rabotu'
    ON_THE_WAY = 'v-puti-k-tochke-dostavki'
    CONTACT_WITH_CUSTOMER = 'kontakt-s-poluchatelem'
    DELIVERED = 'dostavleno'
    SENT_FOR_PREPARATION = 'otpravleno-na-podgotovku'
    PREPARE_TO_SEND = 'podogotovka-k-otpravku'
    READY_TO_SEND = 'gotovo-k-otpravke'
    AT_THE_CALL_POINT = 'na-tochke-vyvoza'
    SMS_SENT = 'kod-otpravlen'
    SCAN_CARD = 'skanirovanie-karty'
    PHOTO_CAPTURING = 'fotografirovanie'
    POST_CONTROL = 'posledkontrol'
    POST_CONTROL_BANK = 'posledkontrol_bank'
    REASSIGNMENT = 'perenaznachenie'
    ON_THE_WAY_TO_EXPORT = 'v-puti-k-tochke-vyvoza'
    VIDEO_IDENTIFICATION = 'videoidentifikatsiia'
    READY_FOR_SHIPMENT = 'gotovo-k-vyvozu'
    PACKED = 'upakovano'
    AT_REVISE = 'na-sverke'
    COURIER_APPOINTED = 'kurer-k-vyvozu-naznachen'
    ACCEPT_IN_GROUP = 'vkliucheno-v-gruppu'
    COURIER_ACCEPTED = 'courier_accepted'
    ACCEPTED_BY_COURIER_SERVICE = 'priniato-kurerskoi-sluzhboi'
    TAKEN_OUT_BY_COURIER = 'vyvezeno-kurerom'
    ISSUED = 'order_delivevred'
    ENDED = 'zaversheno'


class OrderDeliveryStatus(descriptor.Descriptor):
    TRANSFER_TO_CDEK = 'transfer_to_cdek'
    TO_CALL_POINT = 'on-the-way-to-call-point'
    POSTPONED = 'postponed'
    RESCHEDULED = 'rescheduled'
    NONCALL = 'noncall'
    CANCELLED = 'cancelled'
    CANCELED_AT_CLIENT = 'cancelled_at_client'
    BEING_FINALIZED = 'being_finalized'
    # Being finalized at courier service
    BEING_FINALIZED_AT_CS = 'being_finalized_at_cs'
    VIDEO_CHECK_PASSED = 'video_check_passed'
    VIDEO_UNAVAILABLE = 'video_unavailable'
    VIDEO_PC = 'video_postcontrol'
    VIDEO_PC_BEING_FINALIZED = 'video_postcontrol_being_finalized'
    VIDEO_CHECK_FAILED = 'video_check_failed'
    SMS_PC = 'sms_postcontrol'
    SMS_PC_BEING_FINALIZED = 'sms_postcontrol_being_finalized'
    SMS_UNAVAILABLE = 'sms_unavailable'
    SMS_FAILED = 'sms_failed'
    IS_DELIVERED = 'is_delivered'
    UNDER_REVIEW = 'under_review'

    @classmethod
    def main_statuses(cls) -> list:
        return [cls.POSTPONED.value, cls.IS_DELIVERED.value, cls.TO_CALL_POINT.value, cls.CANCELLED.value]


class OrderDeliveryStatusQuery(descriptor.Descriptor):
    TRANSFER_TO_CDEK = 'transfer_to_cdek'
    ON_THE_WAY_TO_CALL_POINT = 'on-the-way-to-call-point'
    POSTPONED = 'postponed'
    RESCHEDULED = 'rescheduled'
    NONCALL = 'noncall'
    CANCELLED = 'cancelled'
    CANCELLED_AT_CLIENT = 'cancelled_at_client'
    POSTCONTROL = 'postcontrol'
    BEING_FINALIZED = 'being_finalized'
    BEING_FINALIZED_AT_CS = 'being_finalized_at_cs'
    BEING_FINALIZED_ON_CANCEL = 'being_finalized_on_cancel'
    IS_DELIVERED = 'is_delivered'
    VIDEO_CHECK_PASSED = 'video_check_passed'
    VIDEO_UNAVAILABLE = 'video_unavailable'
    VIDEO_POSTCONTROL = 'video_postcontrol'
    VIDEO_POSTCONTROL_BEING_FINALIZED = 'video_postcontrol_being_finalized'
    VIDEO_CHECK_FAILED = 'video_check_failed'
    SMS_POSTCONTROL = 'sms_postcontrol'
    SMS_POSTCONTROL_BEING_FINALIZED = 'sms_postcontrol_being_finalized'
    SMS_UNAVAILABLE = 'sms_unavailable'
    SMS_FAILED = 'sms_failed'
    NULL = 'null'


class OrderSMS(descriptor.Descriptor):
    SEND_SMS = 'You must send code first'
    IS_NOT_SUBJECT = 'Order is not subject to sms post-control'
    NOT_MATCH = 'Provided code did not match'
    MAX_LIMIT = 'You have reached maximum sms sending'
    TRY_MAX_LIMIT = 'You have reached maximum sms trying'


class OrderReportFields(descriptor.Descriptor):
    ID = 'id'
    PARTNER_NAME_RU = 'partner_name'
    PRODUCT_NAME = 'product_name'
    AREA_NAME = 'area_name'
    COURIER_FULLNAME = 'courier_fullname'
    COURIER_PHONE = 'courier_phone'
    CURRENT_STATUS = 'current_status'
    SHIPMENT_POINT = 'shipment_point'
    CREATED_AT = 'created at'
    RECEIVER_FULLNAME = 'receiver_fullname'


class OrderReportOrdering(descriptor.Descriptor):
    ID = 'id',
    CREATED_AT = 'created_at'
    CREATED_AT_DESC = '-created_at'
    DELIVERY_TIME = 'delivery_datetime'
    DELIVERY_TIME_DESC = '-delivery_datetime'


class OrderChangeAddressType(descriptor.Descriptor):
    SAVE_COURIER_SAVE_DELIVERY_DATETIME = 'save_courier_save_delivery_datetime'
    NEW_COURIER_SAVE_DELIVERY_DATETIME = 'new_courier_save_delivery_datetime'
    SAVE_COURIER_NEW_DELIVERY_DATETIME = 'save_courier_new_delivery_datetime'
    NEW_COURIER_NEW_DELIVERY_DATETIME = 'new_courier_new_delivery_datetime'
    RESTORE = 'restore'


class OrderChangeAddressReason(descriptor.Descriptor):
    INCORRECT_ADDRESS = 'incorrect_address'
    EMPTY_COORDINATES = 'empty_coordinates'
    CLIENT_CHANGED = 'client_changed'


class CourierService(descriptor.Descriptor):
    CDEK = 'cdek'


__all__ = (
    'CreatedType',
    'OrderChangeAddressType',
    'OrderChangeAddressReason',
    'OrderDeliveryStatus',
    'OrderDeliveryStatusQuery',
    'OrderReportFields',
    'OrderReportOrdering',
    'OrderSearchType',
    'OrderSMS',
    'OrderStatus',
    'OrderType',
    'StatusIcon',
    'StatusSlug',
    'OrderStatusCodes',
    'ProductType',
    'CourierService',
)
