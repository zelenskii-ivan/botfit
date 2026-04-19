# Changelog

## [1.3.0] — 2026-04-19

### Модуль `shelf` (27.04–20.05.2026)

- Cron **`request_shelf_photo`** в `19:30` (`SHELF_ENABLED`, `SHELF_HOUR`, `SHELF_MIN`), сезон через `start_date`/`end_date` в APScheduler.
- **`bot/shelf_vision.py`** — OpenAI Vision `gpt-4o`, JSON остатков; **`bot/weather.py`** — OpenWeatherMap, кэш 3 ч в `shelf.weather`.
- **`bot/shelf_recommendation.py`** — Claude (`ANTHROPIC_API_KEY`) или GPT-4o; **`bot/shelf_pipeline.py`** — цепочка и рассылка в `MANAGER_CHAT_ID` + `GROUP_ID`, кнопка **«✅ Принято»**.
- **`bot/state.py`**: `shelf`, `today_remainders`, `sales_history`, персист **`data/shelf_history.json`**.
- Команды **`/shelf`**, **`/shelf_report`**, **`/shelf_history`**; фото документом при ожидании shelf.
- Опция **`BAKERY_RUN_SHELF_AI`** — после принятого фото выпечки запускается тот же пайплайн (Vision + рекомендация), если сезон полки и задан **`OPENAI_API_KEY`**.
- Зависимости: `openai`, `httpx`, `anthropic`.
