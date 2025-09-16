from .. import enums


class FeedbackStatus(enums.Descriptor):
    NEW = 'new'
    APPROVED = 'approved'
    DECLINED = 'declined'


class AuthorsFeedback(enums.Descriptor):
    RECEIVER = 'receiver'
    SYSTEM = 'system'
    MANAGER = 'manager'
