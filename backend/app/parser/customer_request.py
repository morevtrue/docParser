"""Парсер запроса ТКП (документ от заказчика)."""
from docx import Document
from .base import get_all_paragraphs, get_table_as_pairs, find_in_paragraphs, find_value_by_keywords
from ..models.schemas import CustomerRequest, CustomerRequestItem
from typing import Optional


def _detect_items_table_columns(header_cells: list[str]) -> dict[int, str]:
    """
    Семантически определяет маппинг колонок таблицы номенклатуры по заголовкам.
    Возвращает {col_idx: field_name}.
    """
    mapping = {}
    for i, h in enumerate(header_cells):
        h_lower = h.lower().strip()
        if any(kw in h_lower for kw in ["наименование", "название", "товар"]):
            mapping[i] = "name"
        elif any(kw in h_lower for kw in ["ед. изм", "ед.изм", "единица", "ед."]):
            mapping[i] = "unit"
        elif any(kw in h_lower for kw in ["количество", "кол-во", "кол."]):
            mapping[i] = "quantity"
        elif any(kw in h_lower for kw in ["нмц", "нмц за ед", "нмц, руб"]):
            mapping[i] = "nmc"
        elif any(kw in h_lower for kw in ["артикул", "арт."]):
            mapping[i] = "article"
        elif any(kw in h_lower for kw in ["код позиции", "код"]):
            mapping[i] = "code"
        elif any(kw in h_lower for kw in ["требуемая дата", "дата поставки", "срок"]):
            mapping[i] = "required_date"
        elif h_lower in ("№", "#", "номер", "n"):
            mapping[i] = "number"
    return mapping


def parse_customer_request(doc: Document, source: str = "") -> CustomerRequest:
    """
    Извлекает данные из документа «Запрос ТКП».
    Поддерживает как стандартный формат (параграфы + таблицы),
    так и объединённые поля (Закупка/лот/код, данные в таблице).
    """
    paragraphs = get_all_paragraphs(doc)

    # Собираем все пары ключ-значение из всех таблиц (кроме таблицы номенклатуры)
    all_pairs: list[tuple[str, str]] = []
    items_table_idx = None

    for ti, table in enumerate(doc.tables):
        if not table.rows:
            continue
        header = [c.text.strip().lower() for c in table.rows[0].cells]
        # Таблица номенклатуры — содержит НМЦ или наименование товара
        if any(any(kw in h for kw in ["нмц", "наименование", "артикул"]) for h in header):
            items_table_idx = ti
        else:
            all_pairs.extend(get_table_as_pairs(table))

    def from_para(keywords: list[str]) -> Optional[str]:
        return find_in_paragraphs(paragraphs, keywords)

    def from_table(keywords: list[str]) -> Optional[str]:
        return find_value_by_keywords(all_pairs, keywords)

    # Предмет закупки — из параграфа или таблицы
    purchase_name = from_para(["предмет закупки"]) or from_table(["предмет закупки"])

    # Заказчик
    customer_name = from_para(["заказчик"]) or from_table(["заказчик"])

    # Номер закупки, лот, код лота
    purchase_number = None
    lot = None
    lot_code = None

    # Стандартный формат: параграф "Номер закупки: X    Лот: Y    Код лота: Z"
    for para in paragraphs:
        if "номер закупки" in para.lower():
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

    # Объединённое поле: "Закупка / лот / код" → "TEST-2026-001 / Лот 1 / PE-26-001-L1"
    if not purchase_number:
        combined = from_table(["закупка / лот", "закупка/лот", "номер / лот", "закупка"])
        if combined and "/" in combined:
            parts = [p.strip() for p in combined.split("/")]
            purchase_number = parts[0] if parts else None
            if len(parts) > 1:
                lot = parts[1]
            if len(parts) > 2:
                lot_code = parts[2]
        elif combined:
            purchase_number = combined

    # Срок подачи предложений
    deadline = from_para(["срок подачи"]) or from_table(["срок подачи предложений", "срок подачи"])

    # Место поставки — из параграфа или таблицы
    delivery_place = from_para(["место поставки"]) or from_table(["место поставки", "адрес поставки"])
    if not delivery_place:
        for para in paragraphs:
            if "адрес поставки" in para.lower() or "место поставки" in para.lower():
                if ":" in para:
                    delivery_place = para.split(":", 1)[1].strip()
                    break

    # Срок поставки
    delivery_term = from_para(["срок поставки"]) or from_table(["срок поставки"])
    if not delivery_term:
        for para in paragraphs:
            if "срок поставки" in para.lower() or "требуемый срок поставки" in para.lower():
                if ":" in para:
                    delivery_term = para.split(":", 1)[1].strip()
                    break

    # Условия оплаты
    payment_term = from_para(["оплата"]) or from_table(["условия оплаты", "оплата"])
    if not payment_term:
        for para in paragraphs:
            if "оплата" in para.lower() and (":" in para or "календарных дней" in para.lower()):
                if ":" in para:
                    payment_term = para.split(":", 1)[1].strip()
                else:
                    payment_term = para
                break

    # Гарантийный срок
    warranty = from_para(["гарантийный срок"]) or from_table(["гарантийный срок", "гарантия"])
    if not warranty:
        for para in paragraphs:
            if "гарантийн" in para.lower():
                if ":" in para:
                    warranty = para.split(":", 1)[1].strip()
                else:
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
    if not contact_email:
        # Ищем в таблицах
        for key, value in all_pairs:
            if "контакт" in key.lower() or "email" in key.lower() or "e-mail" in key.lower():
                for part in value.split():
                    if "@" in part:
                        contact_email = part.strip(".,;")
                        break

    # Позиции из таблицы номенклатуры — семантическое определение колонок
    items = []
    if items_table_idx is not None:
        table = doc.tables[items_table_idx]
        rows = table.rows
        if rows:
            header_cells = [c.text.strip() for c in rows[0].cells]
            col_map = _detect_items_table_columns(header_cells)

            for row in rows[1:]:
                cells = [c.text.strip() for c in row.cells]
                if not any(cells):
                    continue

                item_data = {}
                for col_idx, field in col_map.items():
                    if col_idx < len(cells):
                        item_data[field] = cells[col_idx] or None

                # Пропускаем строки без наименования
                if not item_data.get("name"):
                    continue

                # Номер строки — если не найден в колонке, используем порядковый
                if not item_data.get("number"):
                    item_data["number"] = str(len(items) + 1)

                items.append(CustomerRequestItem(
                    number=item_data.get("number"),
                    code=item_data.get("code"),
                    article=item_data.get("article"),
                    name=item_data.get("name"),
                    quantity=item_data.get("quantity"),
                    unit=item_data.get("unit"),
                    nmc=item_data.get("nmc"),
                    required_date=item_data.get("required_date"),
                ))

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
        items=items,
    )
