from . import descriptor


class CourierCategory(descriptor.Descriptor):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'


class CourierState(descriptor.Descriptor):
    COURIERS_REFUSAL_TO_REGISTER = 'couriers refusal to register'
    COURIERS_VIDEO_IDENTIFICATION = 'couriers video identification'
    APPROVAL_OF_ADDING_A_COURIER = 'approval of adding a courier'
    REFUSAL_TO_ADD_TO_THE_COURIER = 'refusal to add to the courier'


class ProfileType(descriptor.Descriptor):
    COURIER = 'courier'
    DISPATCHER = 'dispatcher'
    MANAGER = 'manager'
    BANK_MANAGER = 'bank_manager'
    OWNER = 'owner'
    SERVICE_MANAGER = 'service_manager'
    BRANCH_MANAGER = 'branch_manager'
    PARTNER_BRANCH_MANAGER = 'partner_branch_manager'
    SORTER = 'sorter'
    SUPERVISOR = 'supervisor'
    LOGIST = 'logist'
    CALL_CENTER_MANAGER = 'call_center_manager'
    GENERAL_CALL_CENTER_MANAGER = 'general_call_center_manager'
    SUPPORT = 'support'
