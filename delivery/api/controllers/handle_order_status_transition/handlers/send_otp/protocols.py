from abc import ABC, abstractmethod


class PosTerminalSendOTPProtocol(ABC):

    @abstractmethod
    async def send(self, business_key: str, phone_number: str) -> None:
        pass


class FreedomBankSendOTPProtocol(ABC):

    @abstractmethod
    async def send(self, partner_order_id: str) -> None:
        pass