from api import enums


class OrderGroupStatuses(enums.Descriptor):
    NEW_GROUP = 'new_group'
    READY_FOR_PICKUP = 'ready_for_pickup'
    REVISE = 'revise'
    EXPORTED = 'exported'
    UNDER_REVIEW = 'under_revision'
    COURIER_SERVICE_ACCEPTED = 'courier_service_accepted'
    COURIER_APPOINTED = 'courier_appointed'
