"""Парсер запроса ТКП (документ от заказчика)."""
from docx import Document
from .base import get_all_paragraphs, get_table_as_pairs, find_in_paragraphs, find_value_by_keywords
from ..models.schemas import CustomerRequest
from typing import Optional


def parse_customer_request(doc: Document, source: str = "") -> CustomerRequest:
    """
    Извлекает данные из документа «Запрос ТКП».
    Использует семантический поиск по ключевым словам в параграфах и таблицах.
    """
    paragraphs = get_all_paragraphs(doc)

    # Собираем все пары ключ-значение из всех таблиц
    all_pairs: list[tuple[str, str]] = []
    for table in doc.tables:
        all_pairs.extend(get_table_as_pairs(table))

    def from_para(keywords: list[str]) -> Optional[str]:
        return find_in_paragraphs(paragraphs, keywords)

    def from_table(keywords: list[str]) -> Optional[str]:
        return find_value_by_keywords(all_pairs, keywords)

    # Номер закупки, лот, код лота — в одном параграфе через пробелы
    purchase_number = None
    lot = None
    lot_code = None
    for para in paragraphs:
        if "номер закупки" in para.lower():
            # Формат: "Номер закупки: X    Лот: Y    Код лота: Z"
            parts = para.replace("\t", " ")
            for segment in parts.split("  "):
                segment = segment.strip()
                if ":" not in segment:
                    continue
                k, _, v = segment.partition(":")
                k, v = k.strip().lower(), v.strip()
                if "номер закупки" in k:
                    purchase_number = v
                elif k == "лот":
                    lot = v
                elif "код лота" in k:
                    lot_code = v
            break

    # Заказчик — из параграфа "Заказчик: ..."
    customer_name = from_para(["заказчик"])

    # Предмет закупки
    purchase_name = from_para(["предмет закупки"])

    # Срок подачи предложений
    deadline = from_para(["срок подачи"])

    # Место поставки
    delivery_place = from_para(["место поставки"])

    # Срок поставки
    delivery_term = from_para(["срок поставки"])

    # Условия оплаты — может быть без двоеточия, ищем параграф целиком
    payment_term = from_para(["оплата"])
    if not payment_term:
        for para in paragraphs:
            if "оплата" in para.lower() and "календарных дней" in para.lower():
                payment_term = para
                break

    # Гарантийный срок — может быть без двоеточия
    warranty = from_para(["гарантийный срок"])
    if not warranty:
        for para in paragraphs:
            if "гарантийный срок" in para.lower():
                warranty = para
                break

    # Email контакта
    contact_email = None
    for para in paragraphs:
        if "e-mail:" in para.lower() or "email:" in para.lower():
            for part in para.split():
                if "@" in part:
                    contact_email = part.strip(".,;")
                    break

    return CustomerRequest(
        purchase_name=purchase_name,
        purchase_number=purchase_number,
        lot=lot,
        lot_code=lot_code,
        customer_name=customer_name,
        deadline=deadline,
        delivery_place=delivery_place,
        delivery_term=delivery_term,
        payment_term=payment_term,
        warranty=warranty,
        contact_email=contact_email,
    )
