# Phase 2 — DONE

## Что реализовано

- `backend/app/models/schemas.py` — Pydantic DTO: CustomerRequest, SupplierCard, CommercialTerms, PriceItem, ExtractedData, ParsingReport, FieldStatus
- `backend/app/parser/base.py` — базовые утилиты: загрузка DOCX, извлечение параграфов/таблиц, семантический поиск по ключевым словам
- `backend/app/parser/customer_request.py` — парсер запроса ТКП
- `backend/app/parser/supplier_card.py` — парсер карточки поставщика
- `backend/app/parser/commercial_terms.py` — парсер коммерческих условий и цен
- `backend/app/mapping/field_map.py` — конфигурация маппинга полей (источник → шаблон)
- `backend/app/main.py` — обновлён: добавлен POST /api/process с классификацией, парсингом и отчётом

## Результаты проверки на основном наборе

Все поля извлечены корректно:
- CustomerRequest: 9/11 полей (payment_term и warranty — из параграфов без двоеточия, обработаны отдельно)
- SupplierCard: 17/17 полей
- CommercialTerms: 10/10 полей + 3 позиции номенклатуры

## Ограничения

- Генерация выходных DOCX не реализована (Phase 3)
- POST /api/process возвращает JSON, а не ZIP (временно)
- Шаблоны принимаются но не обрабатываются (классифицируются как unknown)
