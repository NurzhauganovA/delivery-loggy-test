from . import descriptor


class PostControlResolution(descriptor.Descriptor):
    PENDING = 'pending',
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    BANK_ACCEPTED = 'bank_accepted'
    BANK_DECLINED = 'bank_declined'


class PostControlType(descriptor.Descriptor):
    POST_CONTROL = 'post_control'
    CANCELED = 'canceled'
    CANCELED_AT_CLIENT = 'canceled_at_client'


class InputPanType(descriptor.Descriptor):
    MANUALLY = 'manually'
    SCANNED = 'scanned'
