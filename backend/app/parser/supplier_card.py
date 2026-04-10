"""Парсер карточки поставщика."""
from docx import Document
from .base import get_table_as_pairs, find_value_by_keywords
from ..models.schemas import SupplierCard


def parse_supplier_card(doc: Document, source: str = "") -> SupplierCard:
    """
    Извлекает данные из документа «Карточка поставщика».
    Все данные хранятся в таблицах формата ключ-значение.
    """
    all_pairs: list[tuple[str, str]] = []
    for table in doc.tables:
        all_pairs.extend(get_table_as_pairs(table))

    def get(keywords: list[str]) -> str | None:
        return find_value_by_keywords(all_pairs, keywords)

    return SupplierCard(
        full_name=get(["полное наименование"]),
        short_name=get(["краткое наименование"]),
        inn=get(["инн"]),
        kpp=get(["кпп"]),
        ogrn=get(["огрн"]),
        legal_address=get(["юридический адрес"]),
        postal_address=get(["почтовый адрес"]),
        bank=get(["банк"]),
        checking_account=get(["расчётный счёт", "расчетный счет"]),
        correspondent_account=get(["корреспондентский счёт", "корреспондентский счет"]),
        bik=get(["бик"]),
        contact_person=get(["контактное лицо"]),
        email=get(["email", "e-mail"]),
        phone=get(["телефон"]),
        signatory=get(["подписант"]),
        signatory_position=get(["должность подписанта"]),
        signatory_basis=get(["основание полномочий"]),
    )
