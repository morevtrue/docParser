# Phase 2 — TESTS

## Чеклист проверок

| # | Проверка | Команда | Ожидаемый результат | Статус |
|---|----------|---------|---------------------|--------|
| 1 | Парсер CustomerRequest | python тест | Все 11 полей заполнены, 3 позиции НМЦ | ✅ |
| 2 | Парсер SupplierCard | python тест | Все 17 полей заполнены | ✅ |
| 3 | Парсер CommercialTerms | python тест | 10 полей + 3 позиции | ✅ |
| 4 | POST /api/process через Docker | python requests | 200 + ZIP, 3 DOCX + report.json | ✅ |
| 5 | Валидация не-DOCX файла | python requests | 400 + сообщение об ошибке | ✅ |
| 6 | Классификация документов | POST с 6 файлами | Все три типа определены, 3 шаблона заполнены | ✅ |

## Примечания

- Запрос без файлов возвращает 422 (FastAPI validation) вместо 400 — приемлемо для MVP

## Как запустить локальный тест парсеров

```bash
python -c "
import sys; sys.path.insert(0, 'backend')
from docx import Document
from app.parser.customer_request import parse_customer_request
from app.parser.supplier_card import parse_supplier_card
from app.parser.commercial_terms import parse_commercial_terms

cr = parse_customer_request(Document('Основной набор/Документы от заказчика/01_Запрос_ТКП_от_заказчика.docx'))
sc = parse_supplier_card(Document('Основной набор/Документы поставщика/01_Карточка_поставщика.docx'))
ct = parse_commercial_terms(Document('Основной набор/Документы поставщика/02_Коммерческие_условия_и_цены_поставщика.docx'))
print(cr.model_dump())
print(sc.model_dump())
print(ct.model_dump())
"
```
