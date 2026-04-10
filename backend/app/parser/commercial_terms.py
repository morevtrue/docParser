"""Парсер коммерческих условий и цен поставщика."""
from docx import Document
from .base import get_table_as_pairs, find_value_by_keywords
from ..models.schemas import CommercialTerms, PriceItem


def _extract_supplier_currency(value: str) -> tuple[str | None, str | None]:
    """Разбивает 'ООО «НордТехРесурс» / RUB' на (поставщик, валюта)."""
    if "/" in value:
        parts = [p.strip() for p in value.split("/")]
        return parts[0], parts[-1]
    return value, None


def _extract_delivery_warranty(value: str) -> tuple[str | None, str | None]:
    """
    Разбивает объединённое поле поставки/гарантии.
    Ищет гарантию по ключевым словам 'гарантия', 'warranty'.
    """
    delivery = warranty = None
    parts = [p.strip() for p in value.split(";") if p.strip()]
    warranty_parts = []
    delivery_parts = []
    for p in parts:
        if any(kw in p.lower() for kw in ["гарантия", "warranty", "гарантийный"]):
            warranty_parts.append(p)
        else:
            delivery_parts.append(p)
    delivery = "; ".join(delivery_parts) if delivery_parts else None
    warranty = "; ".join(warranty_parts) if warranty_parts else None
    return delivery, warranty


def _detect_price_table_columns(header_cells: list[str]) -> dict[int, str]:
    """
    Семантически определяет маппинг колонок таблицы номенклатуры по заголовкам.
    Возвращает {col_idx: field_name}.
    """
    mapping = {}
    for i, h in enumerate(header_cells):
        h_lower = h.lower().strip()
        if any(kw in h_lower for kw in ["наименование", "название", "товар", "продукция"]):
            mapping[i] = "name"
        elif any(kw in h_lower for kw in ["ед. изм", "ед.изм", "единица", "ед."]):
            mapping[i] = "unit"
        elif any(kw in h_lower for kw in ["количество", "кол-во", "кол."]):
            mapping[i] = "quantity"
        elif any(kw in h_lower for kw in ["цена без ндс", "цена без", "цена"]):
            mapping[i] = "price_without_vat"
        elif any(kw in h_lower for kw in ["сумма без ндс", "сумма без", "итого без", "сумма"]):
            mapping[i] = "total_without_vat"
        elif any(kw in h_lower for kw in ["№", "номер", "#"]):
            mapping[i] = "number"
    return mapping


def parse_commercial_terms(doc: Document, source: str = "") -> CommercialTerms:
    """
    Извлекает данные из документа «Коммерческие условия и цены поставщика».
    Поддерживает как стандартный формат, так и объединённые поля.
    Семантически определяет структуру таблицы номенклатуры.
    """
    tables = doc.tables

    # Ищем таблицу с общими условиями (ключ-значение, не номенклатура)
    general_pairs: list[tuple[str, str]] = []
    items_table_idx = None

    for ti, table in enumerate(tables):
        if not table.rows:
            continue
        header = [c.text.strip().lower() for c in table.rows[0].cells]
        # Таблица номенклатуры — содержит колонку с наименованием товара
        if any(any(kw in h for kw in ["наименование", "название", "товар", "продукция"]) for h in header):
            items_table_idx = ti
        else:
            general_pairs.extend(get_table_as_pairs(table))

    def get(keywords: list[str]) -> str | None:
        return find_value_by_keywords(general_pairs, keywords)

    # Стандартные поля
    supplier_name = get(["поставщик"])
    currency = get(["валюта"])
    vat_rate = get(["ставка ндс", "ндс %", "ставка"])
    offer_validity = get(["срок действия предложения", "срок действия"])
    payment_term = get(["условия оплаты", "оплата"])
    delivery_term = get(["срок поставки", "поставка"])
    warranty = get(["гарантия", "гарантийный срок"])

    # Объединённое поле: поставщик / валюта
    if not supplier_name and not currency:
        combined = get(["поставщик / валюта", "поставщик/валюта"])
        if combined:
            supplier_name, currency = _extract_supplier_currency(combined)

    # Объединённое поле: поставка / гарантия
    if not delivery_term or not warranty:
        combined_dg = get(["поставка / гарантия", "поставка/гарантия", "доставка / гарантия"])
        if combined_dg:
            d, w = _extract_delivery_warranty(combined_dg)
            if not delivery_term:
                delivery_term = d
            if not warranty:
                warranty = w

    # Итоги — ищем во всех парах
    def get_total(keywords: list[str], exclude: list[str] | None = None) -> str | None:
        # Сначала точное совпадение
        for key, value in general_pairs:
            key_lower = key.lower().strip()
            for kw in keywords:
                if key_lower == kw.lower():
                    return value
        # Затем вхождение, с исключением нежелательных ключей
        for key, value in general_pairs:
            key_lower = key.lower()
            if exclude and any(ex in key_lower for ex in exclude):
                continue
            for kw in keywords:
                if kw.lower() in key_lower:
                    return value
        return None

    total_without_vat = get_total(["итого без ндс"])
    # НДС ищем точно или как отдельное слово, исключая строки с "итого"
    vat_amount = get_total(["ндс"], exclude=["итого"])
    total_with_vat = get_total(["итого с ндс"])

    # Таблица номенклатуры — семантическое определение колонок
    items: list[PriceItem] = []
    if items_table_idx is not None:
        table = tables[items_table_idx]
        rows = table.rows
        if rows:
            header_cells = [c.text.strip() for c in rows[0].cells]
            col_map = _detect_price_table_columns(header_cells)

            for row in rows[1:]:
                cells = [c.text.strip() for c in row.cells]
                if not cells or not any(cells):
                    continue
                # Пропускаем строки без данных (итоговые строки и т.п.)
                if not any(c for c in cells if c and not c.isspace()):
                    continue

                item_data = {}
                for col_idx, field in col_map.items():
                    if col_idx < len(cells):
                        item_data[field] = cells[col_idx] or None

                # Пропускаем строки без наименования
                if not item_data.get("name"):
                    continue

                items.append(PriceItem(
                    number=item_data.get("number"),
                    name=item_data.get("name"),
                    unit=item_data.get("unit"),
                    quantity=item_data.get("quantity"),
                    price_without_vat=item_data.get("price_without_vat"),
                    total_without_vat=item_data.get("total_without_vat"),
                ))

    return CommercialTerms(
        supplier_name=supplier_name,
        currency=currency,
        vat_rate=vat_rate,
        offer_validity=offer_validity,
        payment_term=payment_term,
        delivery_term=delivery_term,
        warranty=warranty,
        total_without_vat=total_without_vat,
        vat_amount=vat_amount,
        total_with_vat=total_with_vat,
        items=items,
    )
