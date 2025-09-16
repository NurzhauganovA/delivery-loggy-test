"""
    Временно вынес получения дополнительный headers для callbacks сюда для удобства использования.
    Это не целевое решение.
"""
from api.conf import conf
from typing import Protocol


class CallbacksHeadersProviderProtocol(Protocol):
    """Интерфейс, реализующий метод получения HTTP заголовков в зависимости от партнера"""
    def get_headers(self) -> dict:
        pass


class FreedomBankKZHeadersProvider(CallbacksHeadersProviderProtocol):
    def __init__(self, token: str):
        self.token: str = token

    def get_headers(self,) -> dict:
        return {'Authorization': self.token}


__HEADERS_PROVIDERS: dict[int, CallbacksHeadersProviderProtocol] = {
    conf.freedom_bank.partner_id: FreedomBankKZHeadersProvider(token=conf.freedom_bank_callbacks.token)
}


def get_headers(partner_id: int) -> dict:
    """Метод, возвращающий HTTP заголовки для callbacks методов в зависимости от партнера"""
    headers = {}
    provider = __HEADERS_PROVIDERS.get(partner_id)
    if provider:
        headers.update(provider.get_headers())

    return headers
