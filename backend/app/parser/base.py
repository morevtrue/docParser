"""Базовые утилиты для парсинга DOCX-документов."""
from docx import Document
from docx.table import Table
from typing import Optional


def load_document(path: str) -> Document:
    """Загружает DOCX-документ по пути."""
    return Document(path)


def get_all_paragraphs(doc: Document) -> list[str]:
    """Возвращает все непустые параграфы документа."""
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]


def get_table_as_pairs(table: Table) -> list[tuple[str, str]]:
    """
    Извлекает пары (ключ, значение) из таблицы с двумя колонками.
    Пропускает строки, где меньше двух ячеек или значение пустое.
    """
    pairs = []
    for row in table.rows:
        cells = [c.text.strip() for c in row.cells]
        if len(cells) >= 2 and cells[0] and cells[1]:
            pairs.append((cells[0], cells[1]))
    return pairs


def find_value_by_keywords(
    pairs: list[tuple[str, str]],
    keywords: list[str],
) -> Optional[str]:
    """
    Семантический поиск значения по ключевым словам.
    Ищет строку, в которой ключ содержит хотя бы одно из ключевых слов (без учёта регистра).
    Возвращает первое совпадение или None.
    """
    for key, value in pairs:
        key_lower = key.lower()
        for kw in keywords:
            if kw.lower() in key_lower:
                return value
    return None


def find_in_paragraphs(paragraphs: list[str], keywords: list[str]) -> Optional[str]:
    """
    Ищет в параграфах строку, содержащую ключевое слово, и возвращает текст после двоеточия.
    Например: 'Заказчик: АО «Полярная Энергетика»' → 'АО «Полярная Энергетика»'
    """
    for para in paragraphs:
        para_lower = para.lower()
        for kw in keywords:
            if kw.lower() in para_lower and ":" in para:
                parts = para.split(":", 1)
                value = parts[1].strip()
                if value:
                    return value
    return None


def extract_inline_fields(paragraphs: list[str], fields: dict[str, list[str]]) -> dict[str, Optional[str]]:
    """
    Извлекает несколько полей из параграфов по словарю {поле: [ключевые слова]}.
    Возвращает словарь {поле: значение или None}.
    """
    result = {}
    for field, keywords in fields.items():
        result[field] = find_in_paragraphs(paragraphs, keywords)
    return result
