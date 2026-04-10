from pydantic import BaseModel
from typing import Optional


class CustomerRequest(BaseModel):
    """Данные из запроса ТКП (от заказчика)."""
    purchase_name: Optional[str] = None       # Предмет закупки
    purchase_number: Optional[str] = None     # Номер закупки
    lot: Optional[str] = None                 # Лот
    lot_code: Optional[str] = None            # Код лота
    customer_name: Optional[str] = None       # Заказчик
    deadline: Optional[str] = None            # Срок подачи предложений
    delivery_place: Optional[str] = None      # Место поставки
    delivery_term: Optional[str] = None       # Срок поставки
    payment_term: Optional[str] = None        # Условия оплаты
    warranty: Optional[str] = None            # Гарантийный срок
    contact_email: Optional[str] = None       # Email контакта


class SupplierCard(BaseModel):
    """Данные из карточки поставщика."""
    full_name: Optional[str] = None           # Полное наименование
    short_name: Optional[str] = None          # Краткое наименование
    inn: Optional[str] = None                 # ИНН
    kpp: Optional[str] = None                 # КПП
    ogrn: Optional[str] = None                # ОГРН
    legal_address: Optional[str] = None       # Юридический адрес
    postal_address: Optional[str] = None      # Почтовый адрес
    bank: Optional[str] = None                # Банк
    checking_account: Optional[str] = None    # Расчётный счёт
    correspondent_account: Optional[str] = None  # Корреспондентский счёт
    bik: Optional[str] = None                 # БИК
    contact_person: Optional[str] = None      # Контактное лицо
    email: Optional[str] = None               # Email
    phone: Optional[str] = None               # Телефон
    signatory: Optional[str] = None           # Подписант
    signatory_position: Optional[str] = None  # Должность подписанта
    signatory_basis: Optional[str] = None     # Основание полномочий


class PriceItem(BaseModel):
    """Позиция номенклатуры."""
    number: Optional[str] = None
    name: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[str] = None
    price_without_vat: Optional[str] = None
    total_without_vat: Optional[str] = None


class CommercialTerms(BaseModel):
    """Данные из коммерческих условий и цен поставщика."""
    supplier_name: Optional[str] = None       # Поставщик
    currency: Optional[str] = None            # Валюта
    vat_rate: Optional[str] = None            # Ставка НДС
    offer_validity: Optional[str] = None      # Срок действия предложения
    payment_term: Optional[str] = None        # Условия оплаты
    delivery_term: Optional[str] = None       # Срок поставки
    warranty: Optional[str] = None            # Гарантия
    total_without_vat: Optional[str] = None   # Итого без НДС
    vat_amount: Optional[str] = None          # НДС
    total_with_vat: Optional[str] = None      # Итого с НДС
    items: list[PriceItem] = []               # Позиции номенклатуры


class ExtractedData(BaseModel):
    """Объединённые данные из всех входных документов."""
    customer_request: Optional[CustomerRequest] = None
    supplier_card: Optional[SupplierCard] = None
    commercial_terms: Optional[CommercialTerms] = None


class FieldStatus(BaseModel):
    """Статус одного поля в отчёте."""
    field: str
    found: bool
    value: Optional[str] = None
    source: Optional[str] = None   # имя файла-источника


class ParsingReport(BaseModel):
    """Отчёт об обработке документов."""
    found: list[FieldStatus] = []
    warnings: list[FieldStatus] = []
    errors: list[str] = []
