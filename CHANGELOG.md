# Changelog

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/).

## [1.2.0] — 2026-04-18

### Добавлено

- **Регламент «Санитария»** (`sanitary`): ежедневный чеклист по расписанию (`SANITARY_HOUR`, `SANITARY_MIN`), отключение cron: `SANITARY_ENABLED=false`; ручной запрос `/sanitary`; подтверждение `/sanitary_ok` или кнопка «🧹 Санитария ОК» (reply и inline).
- **Регламент «Оборудование»** (`equipment`): аналогично (`EQUIPMENT_*`, `EQUIPMENT_ENABLED`), команды `/equipment`, `/equipment_ok`, кнопка «🔧 Оборудование ОК».
- Напоминания и эскалация для обоих регламентов (как у остальных чеклистов); записи в состоянии и в **`GET /status`**.
- **База знаний для ИИ:** файл по умолчанию `bot/faq_knowledge.md`; свой путь — переменная **`FAQ_PATH`**.
- Модули **`bot/knowledge.py`** (загрузка FAQ, разбор заголовков для `/topics`) и **`bot/ai_qa.py`** (OpenAI Chat Completions, лимит запросов на пользователя в минуту).
- Команды **`/topics`** (список разделов FAQ) и **`/ask …`** (вопрос по базе знаний); при ответе показывается статус «печатает» (`ChatAction.TYPING`).
- Настройки ИИ в `.env`: **`AI_ENABLED`**, **`OPENAI_API_KEY`**, **`OPENAI_MODEL`**, опционально **`OPENAI_BASE_URL`** (совместимые прокси/API).
- Зависимость **`openai`** в `requirements.txt`.

### Изменено

- Версия приложения **1.2.0** (`bot/__init__.py`); лог старта: `Bakery Bot v1.2.0 …`.
- **`bot/state.py`**, **`bot/status_text.py`**, **`bot/api/main`**: в статусе дня и JSON API добавлены задачи **`sanitary`** и **`equipment`**; `summary.all_done` учитывает их.
- **`bot/handlers/commands.py`**, **`bot/handlers/callbacks.py`**, **`bot/keyboards.py`**: новые команды и callback `cb_sanitary_ok` / `cb_equipment_ok`.
- **`bot/tasks.py`**, **`bot/scheduler.py`**: `request_sanitary`, `request_equipment`, cron-джобы при включённых флагах.
- **`bot/start_message.py`**, **`README.md`**, **`DEPLOY.md`**, **`.env.example`**: описание регламентов, ИИ и переменных окружения.
- **`.dockerignore`**: правило `!bot/faq_knowledge.md`, чтобы Markdown базы знаний попадал в Docker-образ (остальные `*.md` по-прежнему исключены).

### Тесты

- **`tests/test_smoke.py`**: в проверке **`GET /status`** учтены `sanitary` и `equipment`; добавлен **`TestKnowledge`** (`list_topic_titles`).

---

## [1.1.0] — 2026-04-18

### Добавлено

- Команда **`/help`** — дублирует справку **`/start`**.
- Модуль **`bot/status_text.py`** — единое HTML-форматирование статуса для сообщений и inline-кнопки «Статус».
- HTTP API: **`GET /version`**; в **`GET /`** добавлено поле **`version`**; **`GET /status`**: задача **`freezer`**, поля **`done`** и **`status`** по каждой задаче, сводка **`summary.all_done`**.
- Поддержка **видеокружка** (`video_note`) на этапе видео по **молочке** (наряду с обычным видео).
- Функция **`_schedule_reminders`** в **`bot/tasks.py`**: у джобов напоминания/эскалации фиксированные **`id`** и **`replace_existing=True`**, чтобы при повторном ручном запросе не копировались таймеры.
- Документация: **`RELEASE.md`** (чеклист релиза, клонирование без лишних аргументов в `git checkout`), ссылка на репозиторий в **`README.md`**.
- **Дымовые тесты** **`tests/test_smoke.py`**: `unittest` + Starlette **`TestClient`** — `/health`, `/ready`, `/version`, `/`, `/status`, импорт handlers, **`format_day_status_html`**.
- В **`bot/__init__.py`** закреплено **`__version__`** как единый источник номера версии для API и логов.

### Изменено

- **`bot/api/main.py`**: время в ответах — **UTC с timezone** (`datetime.now(timezone.utc)`), не `utcnow()`.
- **`bot/start_message.py`**: заморозка, **`/freezer`**, видеокружок, команды и обязательные работы.
- **`bot/handlers/callbacks.py`**: убраны неиспользуемые импорты задач.

### Исправлено

- После сдачи фото/видео по медиа-задачам выставляется **`status: done`** в состоянии.

---

## [1.0.0] — 2026-04-18

Первая зафиксированная версия в репозитории **botfit**: Telegram-бот кофейни (молочка, выпечка, заморозка, открытие/касса/закрытие, памятка), планировщик APScheduler, FastAPI health/status, Docker и **DEPLOY.md** для Timeweb.
