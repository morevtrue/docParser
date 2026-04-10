"""
Единый конфигурируемый маппинг плейсхолдеров шаблонов → поля DTO.

Структура каждой записи:
  placeholder  — точная строка плейсхолдера в шаблоне (включая скобки)
  source       — имя поля в ExtractedData: "supplier_card" | "customer_request" | "commercial_terms"
  field        — имя поля в соответствующем Pydantic-объекте
  transform    — (опционально) имя трансформации: "shorten_name" | "format_money" | "join_bank" | "join_contact"

Добавление нового поля = одна строка здесь. Код генератора не трогать.
"""

FIELD_MAP: list[dict] = [
    # --- Карточка поставщика ---
    {"placeholder": "[Полное наименование участника]",  "source": "supplier_card", "field": "full_name"},
    {"placeholder": "[Краткое наименование участника]", "source": "supplier_card", "field": "short_name"},
    {"placeholder": "[ИНН]",                            "source": "supplier_card", "field": "inn"},
    {"placeholder": "[КПП]",                            "source": "supplier_card", "field": "kpp"},
    {"placeholder": "[ОГРН]",                           "source": "supplier_card", "field": "ogrn"},
    {"placeholder": "[Юридический адрес]",              "source": "supplier_card", "field": "legal_address"},
    {"placeholder": "[Контактное лицо]",                "source": "supplier_card", "field": "contact_person"},
    {"placeholder": "[E-mail]",                         "source": "supplier_card", "field": "email"},
    {"placeholder": "[Телефон]",                        "source": "supplier_card", "field": "phone"},
    {"placeholder": "[ФИО подписанта]",                 "source": "supplier_card", "field": "signatory",          "transform": "shorten_name"},
    {"placeholder": "[Должность подписанта]",           "source": "supplier_card", "field": "signatory_position"},
    {"placeholder": "[Основание полномочий]",           "source": "supplier_card", "field": "signatory_basis"},

    # Банковские реквизиты — каждый компонент отдельно
    {"placeholder": "[Расчетный счет]",        "source": "supplier_card", "field": "checking_account"},
    {"placeholder": "[Наименование банка]",     "source": "supplier_card", "field": "bank"},
    {"placeholder": "[Корреспондентский счет]", "source": "supplier_card", "field": "correspondent_account"},
    {"placeholder": "[БИК]",                   "source": "supplier_card", "field": "bik"},

    # --- Запрос ТКП ---
    {"placeholder": "[Предмет закупки]",  "source": "customer_request", "field": "purchase_name"},
    {"placeholder": "[Номер закупки]",    "source": "customer_request", "field": "purchase_number"},

    # --- Коммерческие условия ---
    {"placeholder": "[Срок действия предложения, дней]", "source": "commercial_terms", "field": "offer_validity"},
    {"placeholder": "[Итого без НДС]",    "source": "commercial_terms", "field": "total_without_vat", "transform": "format_money"},
    {"placeholder": "[Сумма НДС]",        "source": "commercial_terms", "field": "vat_amount",        "transform": "format_money"},
    {"placeholder": "[Итого с НДС]",      "source": "commercial_terms", "field": "total_with_vat",    "transform": "format_money"},

    # --- Генерируемые значения (не из документов) ---
    {"placeholder": "[Дата в формате «26» марта 2026 года]", "source": "__generated__", "field": "current_date",     "transform": "current_date"},
    {"placeholder": "[Исх. номер заявки]",                   "source": "__generated__", "field": "outgoing_number",  "transform": "outgoing_number"},
]

# Маппинг колонок таблицы номенклатуры (Предложение о цене договора)
# Индекс колонки → поле из PriceItem (или "nmc" — из CustomerRequestItem)
PRICE_TABLE_COLUMNS: dict[int, str] = {
    1: "name",
    2: "unit",
    3: "nmc",               # берётся из customer_request.items[i].nmc
    4: "price_without_vat",
    5: "quantity",
    6: "total_without_vat", # применяется format_money
}
