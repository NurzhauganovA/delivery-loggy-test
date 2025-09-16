from . import descriptor


class InviteStatus(descriptor.Descriptor):
    ACCEPTED = 'accepted'
    PENDING = 'pending'
    UNCONFIRMED = 'unconfirmed'
    INVITED = 'invited'
    REFUSED = 'refused'


class UserSearchType(descriptor.Descriptor):
    FULL_NAME = 'full_name'
    IIN = 'inn'
    PHONE = 'phone'