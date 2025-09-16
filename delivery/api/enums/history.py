from .. import enums


class HistoryModelName(enums.Descriptor):
    PROFILE = 'Profile'
    USER = 'User'
    ITEM = 'Item'
    ORDER = 'Order'
    PARTNER = 'Partner'
    PARTNER_SHIPMENT_POINTS = 'PartnerShipmentPoints'
    IMPORT_ORDER = 'OrderImport'
    ORDER_GROUP = 'OrderGroup'
    PARTNER_SETTINGS = 'PartnerSetting'
    ORDER_CHAIN = 'OrderChain'


class InitiatorType(enums.Descriptor):
    IMPORT = 'Import'
    USER = 'User'
    EXTERNAL_SERVICE = 'ExternalService'


class ActionType(enums.Descriptor):
    CREATE_COMMENT = 'create_comment'
