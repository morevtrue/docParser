"""Парсер коммерческих условий и цен поставщика."""
from docx import Document
from .base import get_table_as_pairs, find_value_by_keywords
from ..models.schemas import CommercialTerms, PriceItem


def parse_commercial_terms(doc: Document, source: str = "") -> CommercialTerms:
    """
    Извлекает данные из документа «Коммерческие условия и цены поставщика».
    Таблица 0 — общие условия (ключ-значение).
    Таблица 1 — номенклатура и цены.
    Таблица 2 — итоги.
    """
    tables = doc.tables

    # Таблица 0: общие условия
    general_pairs: list[tuple[str, str]] = []
    if len(tables) > 0:
        general_pairs = get_table_as_pairs(tables[0])

    def get(keywords: list[str]) -> str | None:
        return find_value_by_keywords(general_pairs, keywords)

    # Таблица 1: номенклатура
    items: list[PriceItem] = []
    if len(tables) > 1:
        rows = tables[1].rows
        # Первая строка — заголовок, пропускаем
        for row in rows[1:]:
            cells = [c.text.strip() for c in row.cells]
            if len(cells) >= 6 and cells[0].isdigit():
                items.append(PriceItem(
                    number=cells[0],
                    name=cells[1],
                    unit=cells[2],
                    quantity=cells[3],
                    price_without_vat=cells[4],
                    total_without_vat=cells[5],
                ))

    # Таблица 2: итоги
    totals_pairs: list[tuple[str, str]] = []
    if len(tables) > 2:
        totals_pairs = get_table_as_pairs(tables[2])

    def get_total(keywords: list[str]) -> str | None:
        # Ищем точное совпадение (без вхождения подстроки в другие строки)
        for key, value in totals_pairs:
            key_lower = key.lower().strip()
            for kw in keywords:
                if key_lower == kw.lower():
                    return value
        return find_value_by_keywords(totals_pairs, keywords)

    return CommercialTerms(
        supplier_name=get(["поставщик"]),
        currency=get(["валюта"]),
        vat_rate=get(["ставка ндс"]),
        offer_validity=get(["срок действия предложения"]),
        payment_term=get(["условия оплаты"]),
        delivery_term=get(["срок поставки"]),
        warranty=get(["гарантия"]),
        total_without_vat=get_total(["итого без ндс"]),
        vat_amount=get_total(["ндс"]),
        total_with_vat=get_total(["итого с ндс"]),
        items=items,
    )
