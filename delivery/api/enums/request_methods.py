from .. import enums


class RequestMethods(enums.Descriptor):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'

    @classmethod
    def get_all(cls):
        return [
            cls.GET,
            cls.POST,
            cls.PUT,
            cls.DELETE,
            cls.PATCH,
            cls.HEAD,
            cls.OPTIONS,
        ]
