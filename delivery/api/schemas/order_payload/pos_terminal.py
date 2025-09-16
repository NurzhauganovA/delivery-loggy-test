from pydantic import constr, BaseModel, validator

from decimal import Decimal

from api.domain.money.money import Money


class POSTerminalPayload(BaseModel):
    # Подключена ли услуга рассрочка/кредит
    is_installment_enabled: bool = False
    # Кредитный лимит (Да/Нет)
    is_installment_limit: bool = False
    # Модель POS-терминала
    model: constr(min_length=1, max_length=10) | None
    # Серийный номер
    serial_number: constr(min_length=1, max_length=20) | None
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
    # Инвентарный номер
    inventory_number: constr(min_length=1, max_length=50) | None
    # Стоимость с тиынами
    sum: Decimal | None

    @validator('sum')
    def validate_sum(cls, value: Decimal | None) -> Decimal | None:
        """Валидация значения sum"""
        if not value:
            return value

        try:
            money = Money(amount=value)
        except ValueError:
            raise ValueError('sum is too large')

        return money.amount
