from abc import ABC, abstractmethod


class PosTerminalVerifyOTPProtocol(ABC):

    @abstractmethod
    async def verify(        self,
        business_key: str,
        phone_number: str,
        otp_code: str,
        courier_full_name: str,
    ) -> None:
        pass


class FreedomBankVerifyOTPProtocol(ABC):

    @abstractmethod
    async def verify(self, partner_order_id: str, otp_code: str) -> None:
        pass