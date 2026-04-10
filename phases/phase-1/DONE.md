# Phase 1 — DONE

## Что реализовано

- `docker-compose.yml` — два сервиса (backend, frontend) в общей сети
- `backend/Dockerfile` — Python 3.11-slim, uvicorn с --reload
- `backend/requirements.txt` — fastapi, uvicorn, python-docx, pydantic, python-multipart
- `backend/app/main.py` — FastAPI app с `GET /api/health` → `{"status": "ok"}`
- `frontend/Dockerfile` — Node 20-alpine, npm install, vite dev server
- `frontend/package.json` — React 18 + TypeScript + Vite
- `frontend/vite.config.ts` — proxy `/api/*` → `http://backend:8000`
- `frontend/index.html` — точка входа
- `frontend/src/main.tsx` — монтирование React
- `frontend/src/App.tsx` — страница-заглушка

## Ограничения

- shadcn/ui не инициализирован через CLI — будет выполнено в Phase 4 при разработке UI.
  Сейчас фронтенд — чистый React-скелет без компонентов shadcn.
- Парсинг, генерация, загрузка файлов — не реализованы (Phase 2–3).
- База данных отсутствует (не требуется по спецификации).

## Что не входило в фазу

- Парсинг DOCX
- Генерация выходных документов
- UI компоненты
- CI/CD
