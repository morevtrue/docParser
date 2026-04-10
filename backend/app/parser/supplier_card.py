"""Парсер карточки поставщика."""
import re
from docx import Document
from .base import get_table_as_pairs, find_value_by_keywords
from ..models.schemas import SupplierCard


def _split_combined(value: str, sep: str = "/") -> list[str]:
    """Разбивает объединённое значение по разделителю, очищает пробелы."""
    return [v.strip() for v in value.split(sep) if v.strip()]


def _extract_inn_kpp_ogrn(value: str) -> tuple[str | None, str | None, str | None]:
    """
    Извлекает ИНН, КПП, ОГРН из строки вида '7705123456 / 770501001 / 1127746123456'.
    ИНН — 10 или 12 цифр, КПП — 9 цифр, ОГРН — 13 или 15 цифр.
    """
    parts = _split_combined(value)
    inn = kpp = ogrn = None
    for p in parts:
        digits = re.sub(r"\D", "", p)
        if len(digits) in (10, 12) and inn is None:
            inn = digits
        elif len(digits) == 9 and kpp is None:
            kpp = digits
        elif len(digits) in (13, 15) and ogrn is None:
            ogrn = digits
    return inn, kpp, ogrn


def _extract_signatory_parts(value: str) -> tuple[str | None, str | None, str | None]:
    """
    Извлекает ФИО, должность, основание из строки вида
    'Иванов Иван Иванович, Генеральный директор, Устав'.
    """
    parts = [p.strip() for p in value.split(",") if p.strip()]
    signatory = parts[0] if len(parts) > 0 else None
    position = parts[1] if len(parts) > 1 else None
    basis = parts[2] if len(parts) > 2 else None
    return signatory, position, basis


def _extract_name_parts(value: str) -> tuple[str | None, str | None]:
    """
    Извлекает краткое и полное наименование из строки вида
    'ООО «НордТехРесурс» / Общество с ограниченной ответственностью «НордТехРесурс»'.
    """
    parts = _split_combined(value)
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, parts[0] if parts else None


def parse_supplier_card(doc: Document, source: str = "") -> SupplierCard:
    """
    Извлекает данные из документа «Карточка поставщика».
    Поддерживает как стандартный формат (отдельные поля),
    так и объединённые поля (ИНН/КПП/ОГРН, краткое/полное наименование и т.д.).
    """
    all_pairs: list[tuple[str, str]] = []
    for table in doc.tables:
        all_pairs.extend(get_table_as_pairs(table))

    def get(keywords: list[str]) -> str | None:
        return find_value_by_keywords(all_pairs, keywords)

    # Сначала ищем объединённые поля (более специфичные ключи)
    # Объединённое поле: краткое / полное наименование
    full_name = None
    short_name = None
    combined_name = get(["краткое / полное", "полное / краткое"])
    if combined_name and "/" in combined_name:
        short_name, full_name = _extract_name_parts(combined_name)
    else:
        full_name = get(["полное наименование"])
        short_name = get(["краткое наименование"])

    # Объединённое поле: ИНН / КПП / ОГРН
    inn = kpp = ogrn = None
    combined_ids = get(["инн / кпп / огрн", "инн / кпп", "инн/кпп/огрн", "инн/кпп"])
    if combined_ids:
        inn, kpp, ogrn = _extract_inn_kpp_ogrn(combined_ids)
    else:
        inn = get(["инн"])
        kpp = get(["кпп"])
        ogrn = get(["огрн"])

    # Объединённое поле: подписант / должность / основание
    signatory = signatory_position = signatory_basis = None
    combined_sig = get(["подписант / должность", "подписант/должность"])
    if combined_sig:
        signatory, signatory_position, signatory_basis = _extract_signatory_parts(combined_sig)
    else:
        signatory = get(["подписант"])
        signatory_position = get(["должность подписанта"])
        signatory_basis = get(["основание полномочий"])

    # Email: стандартный или с уточнением
    email = get(["email для закупок", "e-mail для закупок"]) or get(["email", "e-mail"])

    return SupplierCard(
        full_name=full_name,
        short_name=short_name,
        inn=inn,
        kpp=kpp,
        ogrn=ogrn,
        legal_address=get(["юридический адрес"]),
        postal_address=get(["почтовый адрес"]),
        bank=get(["банк"]),
        checking_account=get(["расчётный счёт", "расчетный счет"]),
        correspondent_account=get(["корреспондентский счёт", "корреспондентский счет"]),
        bik=get(["бик"]),
        contact_person=get(["контактное лицо"]),
        email=email,
        phone=get(["телефон"]),
        signatory=signatory,
        signatory_position=signatory_position,
        signatory_basis=signatory_basis,
    )
