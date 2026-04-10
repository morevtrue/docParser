"""
Маппинг полей: какие поля из каких документов берутся для заполнения шаблонов.
Структура: {поле_шаблона: {source: тип_документа, field: поле_DTO}}
"""

FIELD_MAP: dict[str, dict] = {
    # --- Из карточки поставщика ---
    "supplier_full_name":        {"source": "supplier_card", "field": "full_name"},
    "supplier_short_name":       {"source": "supplier_card", "field": "short_name"},
    "supplier_inn":              {"source": "supplier_card", "field": "inn"},
    "supplier_kpp":              {"source": "supplier_card", "field": "kpp"},
    "supplier_ogrn":             {"source": "supplier_card", "field": "ogrn"},
    "supplier_legal_address":    {"source": "supplier_card", "field": "legal_address"},
    "supplier_postal_address":   {"source": "supplier_card", "field": "postal_address"},
    "supplier_bank":             {"source": "supplier_card", "field": "bank"},
    "supplier_checking_account": {"source": "supplier_card", "field": "checking_account"},
    "supplier_corr_account":     {"source": "supplier_card", "field": "correspondent_account"},
    "supplier_bik":              {"source": "supplier_card", "field": "bik"},
    "supplier_contact_person":   {"source": "supplier_card", "field": "contact_person"},
    "supplier_email":            {"source": "supplier_card", "field": "email"},
    "supplier_phone":            {"source": "supplier_card", "field": "phone"},
    "supplier_signatory":        {"source": "supplier_card", "field": "signatory"},
    "supplier_signatory_position": {"source": "supplier_card", "field": "signatory_position"},
    "supplier_signatory_basis":  {"source": "supplier_card", "field": "signatory_basis"},

    # --- Из запроса ТКП ---
    "purchase_name":             {"source": "customer_request", "field": "purchase_name"},
    "purchase_number":           {"source": "customer_request", "field": "purchase_number"},
    "purchase_lot":              {"source": "customer_request", "field": "lot"},
    "purchase_lot_code":         {"source": "customer_request", "field": "lot_code"},
    "customer_name":             {"source": "customer_request", "field": "customer_name"},
    "deadline":                  {"source": "customer_request", "field": "deadline"},
    "delivery_place":            {"source": "customer_request", "field": "delivery_place"},
    "delivery_term":             {"source": "customer_request", "field": "delivery_term"},
    "payment_term":              {"source": "customer_request", "field": "payment_term"},
    "warranty":                  {"source": "customer_request", "field": "warranty"},

    # --- Из коммерческих условий ---
    "commercial_currency":       {"source": "commercial_terms", "field": "currency"},
    "commercial_vat_rate":       {"source": "commercial_terms", "field": "vat_rate"},
    "commercial_offer_validity": {"source": "commercial_terms", "field": "offer_validity"},
    "commercial_total_no_vat":   {"source": "commercial_terms", "field": "total_without_vat"},
    "commercial_vat_amount":     {"source": "commercial_terms", "field": "vat_amount"},
    "commercial_total_with_vat": {"source": "commercial_terms", "field": "total_with_vat"},
}
