from pydantic import (
    constr,
    BaseModel,
    validator,
)

from api.domain.pan import Pan


class POSTerminalPayload(BaseModel):
    # Подключена ли услуга рассрочка/кредит
    is_installment_enabled: bool = False
    # Кредитный лимит (Да/Нет)
    is_installment_limit: bool = False
    # Наименование ИП/ТОО
    company_name: constr(min_length=1, max_length=100)
    merchant_id: constr(min_length=8, max_length=20)
    terminal_id: constr(min_length=8, max_length=20)
    # Название торговой точки
    store_name: constr(min_length=1, max_length=100) | None
    # Филиал
    branch_name: constr(min_length=1, max_length=100)
    mcc_code: constr(min_length=4, max_length=4)
    oked_code: constr(min_length=1, max_length=20)
    oked_text: constr(min_length=1, max_length=200)
    # Номер основной заявки
    request_number_ref: constr(min_length=1, max_length=50) | None
    pan: str | None

    @validator('pan')
    def mask_pan(cls, pan: str | None) -> str | None:
        if pan:
            return Pan(value=pan).get_masked()

        return None
