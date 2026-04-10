# Руководство по хукам

Хуки — это автоматические триггеры, которые запускают агента или команду
при определённом событии в IDE (Kiro).

Файлы хуков хранятся в `.kiro/hooks/*.json` в корне проекта.

Называй файлы с числовым префиксом — это определяет порядок выполнения
при одном событии: `01-post-write-review.json`, `02-pre-task.json` и т.д.

---

## Структура файла хука

```json
{
  "name": "Название хука",
  "version": "1.0.0",
  "description": "Что делает хук (опционально)",
  "when": {
    "type": "тип события",
    "patterns": ["glob паттерны — только для файловых событий"],
    "toolTypes": ["категории инструментов — только для pre/postToolUse"]
  },
  "then": {
    "type": "askAgent или runCommand",
    "prompt": "промпт для агента (только для askAgent)",
    "command": "команда (только для runCommand)"
  }
}
```

---

## Типы событий (when.type)

| Событие             | Когда срабатывает                   | Требует     |
|---------------------|-------------------------------------|-------------|
| `fileEdited`        | Пользователь сохранил файл          | `patterns`  |
| `fileCreated`       | Создан новый файл                   | `patterns`  |
| `fileDeleted`       | Удалён файл                         | `patterns`  |
| `preToolUse`        | Перед вызовом инструмента агентом   | `toolTypes` |
| `postToolUse`       | После вызова инструмента агентом    | `toolTypes` |
| `preTaskExecution`  | Перед началом задачи в спеке        | —           |
| `postTaskExecution` | После завершения задачи в спеке     | —           |
| `promptSubmit`      | При отправке сообщения агенту       | —           |
| `agentStop`         | При завершении сессии агента        | —           |
| `userTriggered`     | Ручной запуск пользователем         | —           |

---

## Категории инструментов (toolTypes)

Используются только для `preToolUse` и `postToolUse`:

| Категория | Что включает                  |
|-----------|-------------------------------|
| `read`    | Чтение файлов                 |
| `write`   | Запись и изменение файлов     |
| `shell`   | Выполнение команд в терминале |
| `web`     | Веб-поиск и fetch             |
| `spec`    | Работа со спеками             |
| `*`       | Все инструменты               |

---

## Важные нюансы

**preToolUse и циклы** — хук `preToolUse` может создать бесконечный цикл,
если агент внутри хука снова вызывает тот же инструмент. Kiro обнаруживает
такие циклы и пропускает вложенные вызовы, но проектируй хуки осторожно.

**Промпты хуков** — пиши конкретно: что проверить, какие файлы прочитать,
что вернуть. Расплывчатые промпты дают расплывчатые результаты.

**Роли агентов** — каждый хук явно указывает агенту прочитать нужный файл
из `agents/`, чтобы принять правильную роль и формат ответа.

---

## Активные хуки проекта

### 01-post-write-review.json
`postToolUse → write` — после записи файла специализированный агент проверяет код.
Автоматически определяет тип файла (frontend/backend) и применяет нужный чеклист.

```json
{
  "name": "Post-write Specialist Review",
  "version": "1.0.0",
  "description": "После записи файла — специализированный агент проверяет код по типу файла",
  "when": {
    "type": "postToolUse",
    "toolTypes": ["write"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "Посмотри на только что записанный файл и определи его тип:\n\n- Если это frontend-файл (*.tsx, *.jsx, *.ts с компонентами, *.css, *.scss) — прочитай agents/frontend.md и действуй как Frontend Senior Agent.\n\n- Если это backend-файл (*.go, *.py, *.java, *.rs, *.ts с сервисами/контроллерами/репозиториями) — прочитай agents/backend.md и действуй как Backend Senior Agent.\n\n- Если тип неоднозначен — прочитай оба файла и примени оба чеклиста.\n\nВыведи результат в формате соответствующего агента."
  }
}
```

---

### 02-pre-task.json
`preTaskExecution` — Product-агент проверяет задачу до старта.

```json
{
  "name": "Pre-task Product Check",
  "version": "1.0.0",
  "description": "Перед началом задачи — Product-агент проверяет понимание и соответствие требованиям",
  "when": {
    "type": "preTaskExecution"
  },
  "then": {
    "type": "askAgent",
    "prompt": "Прочитай agents/product.md и действуй как Product Agent в режиме preTaskExecution. Прочитай WHAT_TO_DO.md текущей фазы и sources-of-truth/BUSINESS_SPEC.md. Проверь понимание задачи, соответствие бизнес-логике, границы фазы. Если есть неоднозначности — задай вопросы до начала реализации."
  }
}
```

---

### 03-post-task-qa.json
`postTaskExecution` — QA-агент проходит чеклист из TESTS.md.

```json
{
  "name": "Post-task QA Checklist",
  "version": "1.0.0",
  "description": "После завершения задачи — QA-агент проходит чеклист из TESTS.md",
  "when": {
    "type": "postTaskExecution"
  },
  "then": {
    "type": "askAgent",
    "prompt": "Прочитай agents/qa.md и действуй как QA Agent. Открой TESTS.md текущей фазы и пройди весь чеклист. Выведи результат с приоритетами 🔴🟡🟢."
  }
}
```

---

### 04-post-task-product.json
`postTaskExecution` — Product-агент проверяет соответствие требованиям после завершения.

```json
{
  "name": "Post-task Product Review",
  "version": "1.0.0",
  "description": "После завершения задачи — Product-агент проверяет соответствие требованиям",
  "when": {
    "type": "postTaskExecution"
  },
  "then": {
    "type": "askAgent",
    "prompt": "Прочитай agents/product.md и действуй как Product Agent в режиме postTaskExecution. Прочитай WHAT_TO_DO.md, DONE.md и BUSINESS_SPEC.md. Выведи результат: Статус ✅/⚠️/❌, Что проверено, Замечания, Вопросы."
  }
}
```

---

### 05-session-summary.json
`agentStop` — агент заполняет DONE.md при завершении сессии.

```json
{
  "name": "Session Summary",
  "version": "1.0.0",
  "description": "При завершении сессии — агент заполняет DONE.md текущей фазы",
  "when": {
    "type": "agentStop"
  },
  "then": {
    "type": "askAgent",
    "prompt": "Сессия завершена. Заполни DONE.md текущей фазы: что реализовано, ограничения, что не вошло, незакрытые вопросы."
  }
}
```

---

### 06-product-review.json
`userTriggered` — ручной запуск полного product-ревью фазы.

```json
{
  "name": "Product Review (Manual)",
  "version": "1.0.0",
  "description": "Ручной запуск: Product-агент критично проверяет результат фазы",
  "when": {
    "type": "userTriggered"
  },
  "then": {
    "type": "askAgent",
    "prompt": "Прочитай agents/product.md и действуй строго как Product Agent. Прочитай WHAT_TO_DO.md, DONE.md, BUSINESS_SPEC.md и ARCHITECTURE.md. Сделай полный обзор фазы. Выведи результат: Статус ✅/⚠️/❌, Что проверено, Замечания, Вопросы."
  }
}
```
