import enum


class TokenTypeHint(str, enum.Enum):
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'

    def __str__(self):
        return str(self.value)
