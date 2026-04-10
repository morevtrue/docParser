# Phase 2 — TESTS

## Чеклист проверок

| # | Проверка | Команда | Ожидаемый результат | Статус |
|---|----------|---------|---------------------|--------|
| 1 | Парсер CustomerRequest | python тест (см. ниже) | Все поля заполнены | ✅ |
| 2 | Парсер SupplierCard | python тест | Все 17 полей заполнены | ✅ |
| 3 | Парсер CommercialTerms | python тест | 10 полей + 3 позиции | ✅ |
| 4 | POST /api/process через Swagger | docker compose up + /docs | JSON с extracted + report | ⬜ |
| 5 | Валидация не-DOCX файла | curl с .txt файлом | 400 Bad Request | ⬜ |
| 6 | Классификация документов | POST с тремя файлами | Все три типа определены | ⬜ |

## Как запустить локальный тест парсеров

```bash
cd C:\dev\homelio_test
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
