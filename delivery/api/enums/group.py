from . import descriptor


class GroupAction(descriptor.Descriptor):
    USER_ADD = 'user_add'
    USER_REMOVE = 'user_remove'
    PERM_ADD = 'perm_add'
    PERM_REMOVE = 'perm_remove'
