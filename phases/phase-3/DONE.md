# Phase 3 — DONE

## Что реализовано

- `backend/app/mapping/field_map.py` — единый конфигурируемый маппинг:
  - `FIELD_MAP` — список записей {placeholder, source, field, transform?}
  - `PRICE_TABLE_COLUMNS` — маппинг колонок таблицы номенклатуры
  - Добавление нового поля = одна строка в конфиге, без правки кода генератора

- `backend/app/generator/filler.py` — динамический генератор:
  - Сканирует шаблон, находит все `[...]` плейсхолдеры
  - Ищет каждый в FIELD_MAP, извлекает значение из DTO, применяет трансформацию
  - `fill_template()` — универсальное заполнение
  - `fill_price_template()` — таблица номенклатуры + стандартный механизм
  - Трансформации: `shorten_name`, `format_money`, `current_date`, `outgoing_number`
  - Возвращает (Document, log) с found / warnings / unmapped

- `backend/app/models/schemas.py` — поле `unmapped` в `ParsingReport`

- `backend/app/main.py` — полный pipeline: парсинг → генерация → ZIP + report.json

## Результаты на основном наборе

| Шаблон | found | warnings | unmapped |
|--------|-------|----------|----------|
| Анкета участника | 15 | 0 | 0 |
| Заявка на участие | 8 | 0 | 0 |
| Предложение о цене | 7 | 0 | 0 |

## Ограничения

- Счётчик исходящих номеров хранится в памяти, сбрасывается при рестарте
- Форматирование сохраняется через первый run параграфа (best effort)
- Контрольный набор — Phase 5
