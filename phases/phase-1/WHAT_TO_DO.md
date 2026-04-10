# Phase 1 — Инфраструктура и скелет проекта

**Статус:** ✅ Завершена

---

## Цель фазы

Поднять рабочее окружение: Docker Compose, скелет бэкенда (FastAPI) и фронтенда (React + shadcn),
health-check эндпоинт. После этой фазы `docker compose up` запускает оба контейнера,
фронтенд открывается в браузере, бэкенд отвечает на `/api/health`.

---

## Задачи

1. Создать структуру проекта:
   - `docker-compose.yml` (frontend + backend)
   - `backend/Dockerfile`
   - `backend/requirements.txt` (fastapi, uvicorn, python-docx, pydantic)
   - `backend/app/main.py` (FastAPI app с `GET /api/health`)
   - `frontend/Dockerfile`
   - `frontend/package.json`
   - `frontend/vite.config.ts` (proxy /api/* на бэкенд)
   - `frontend/src/App.tsx` (заглушка)

2. Настроить Docker Compose:
   - Сервис `backend`: Python, порт 8000
   - Сервис `frontend`: Vite dev server, порт 5173
   - Сеть между контейнерами

3. Инициализировать React + shadcn:
   - Использовать официальную инструкцию: https://ui.shadcn.com/docs/installation
   - НЕ писать конфиги вручную — использовать CLI (`npx shadcn@latest init` и т.д.)
   - Vite + React + TypeScript
   - Базовая страница-заглушка

4. Проверить:
   - `docker compose up --build` запускается без ошибок
   - `GET /api/health` → `{"status": "ok"}`
   - Фронтенд открывается в браузере на `http://localhost:5173`

---

## Ограничения

- НЕ реализуем парсинг, генерацию или загрузку файлов — только скелет.
- НЕ добавляем базу данных — она не нужна.
- НЕ настраиваем CI/CD.

---

## Ссылки

- Архитектура: `sources-of-truth/ARCHITECTURE.md`
- Технический стек: `sources-of-truth/TECH_SPEC.md`
