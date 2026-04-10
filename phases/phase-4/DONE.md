# Phase 4 — DONE

## Что реализовано

### Инфраструктура shadcn/ui (ручная установка)
- Установлены: `tailwindcss`, `@tailwindcss/vite`, `tw-animate-css`, `clsx`, `tailwind-merge`, `lucide-react`
- Установлены radix-ui примитивы: `@radix-ui/react-dialog`, `@radix-ui/react-separator`, `@radix-ui/react-slot`
- `frontend/src/styles/globals.css` — CSS-переменные темы (neutral)
- `frontend/src/lib/utils.ts` — утилита `cn()`
- `frontend/components.json` — конфиг shadcn
- `vite.config.ts` — добавлен `@tailwindcss/vite` плагин и alias `@/*`
- `tsconfig.app.json` — добавлены `baseUrl` и `paths` для alias

### Компоненты shadcn/ui (`frontend/src/components/ui/`)
- `button.tsx` — Button с вариантами (default, outline, ghost, destructive, secondary)
- `card.tsx` — Card, CardHeader, CardTitle, CardContent, CardFooter
- `dialog.tsx` — Dialog с overlay, close-кнопкой
- `badge.tsx` — Badge с вариантами (success, warning, destructive, outline)
- `separator.tsx` — Separator (horizontal/vertical)
- `alert.tsx` — Alert с вариантами (default, destructive, warning, success)

### UI (`frontend/src/App.tsx`)
- Три зоны загрузки: "Документы от заказчика", "Документы поставщика", "Шаблоны"
- Drag & drop + file picker для каждой зоны
- Клиентская валидация: только .docx (по расширению и MIME-type)
- Список загруженных файлов с кнопкой удаления
- Кнопка "Обработать" (disabled если нет файлов)
- Все состояния: empty → loading → success / error
- Отображение отчёта: found / warnings / unmapped / errors
- Кнопка "Скачать результат" (ZIP)
- Кнопка "Обработать другие документы" (сброс)
- Модальное окно при загрузке не-DOCX файла
- Чтение `report.json` из ZIP-ответа через `jszip`

## Ограничения
- shadcn CLI не работал (ошибка чтения конфига) — компоненты добавлены вручную
- Отчёт читается из `report.json` внутри ZIP; если файл отсутствует — показывается успех без деталей
