# Bakery Bot — бот контроля кофейни/пекарни

Репозиторий: [github.com/zelenskii-ivan/botfit](https://github.com/zelenskii-ivan/botfit)

**Версия:** 1.1.0 (см. [CHANGELOG.md](CHANGELOG.md))

Telegram-бот для напоминаний и контроля работы: молочка, выпечка, заморозка, чеклисты открытия/закрытия.

📖 **Подробная инструкция:** [ИНСТРУКЦИЯ.md](ИНСТРУКЦИЯ.md)

## Функции

- **Молочка** (Вт/Чт/Сб): запрос фото + видео полки
- **Выпечка** (ежедневно): запрос фото витрины
- **Заморозка** (ежедневно): фото витрины/морозилки
- **Открытие** (ежедневно): чеклист открытия смены
- **Закрытие** (ежедневно): чеклист закрытия смены
- Напоминания и эскалация при невыполнении
- API для health check и мониторинга

## Установка

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env: BOT_TOKEN, GROUP_ID
```

## Запуск

```bash
python main.py
```

## Деплой на Timeweb Cloud

### Вариант 1: Docker

```bash
docker compose up -d
```

API доступен на порту 8080: `GET /health`, `GET /version`, `GET /status`

### Вариант 2: VPS + systemd

1. Создайте VPS в Timeweb Cloud
2. Скопируйте проект: `rsync -avz . user@server:~/bakery-bot/`
3. На сервере: создайте `.env`, настройте venv
4. Установите systemd unit: `sudo cp deploy/bakery-bot.service /etc/systemd/system/`
5. Отредактируйте пути в unit-файле
6. `sudo systemctl enable bakery-bot && sudo systemctl start bakery-bot`

### Health Check и мониторинг

- `GET /health` — для load balancer
- `GET /ready` — readiness probe
- `GET /version` — номер версии после деплоя
- `GET /status` — статус задач за день (`summary.all_done`, задача `freezer`, поля `done` по задачам)

## Команды бота

| Команда | Описание |
|---------|----------|
| /start, /help | Справка |
| /id | Показать chat_id группы |
| /milk | Запросить молочку вручную |
| /bakery | Запросить выпечку вручную |
| /freezer | Запросить заморозку вручную |
| /opening | Запросить чеклист открытия |
| /cash | Запросить подсчёт наличных |
| /closing | Запросить чеклист закрытия |
| /status | Статус за сегодня |
| /memo | Памятка с обязательными работами |
| /opening_ok | Подтвердить чеклист открытия |
| /cash_ok | Подтвердить подсчёт наличных |
| /closing_ok | Подтвердить чеклист закрытия |

📦 **Деплой и релиз:** [DEPLOY.md](DEPLOY.md), [RELEASE.md](RELEASE.md)

**Уведомления:** памятка отправляется 2 раза в день (9:00 и 15:00) с обязательными работами.

## Структура проекта

```
botrop/
├── bot/           # Пакет бота
│   ├── api/       # FastAPI (health, status)
│   ├── handlers/  # Обработчики команд и контента
│   ├── config.py
│   ├── state.py
│   ├── tasks.py
│   ├── scheduler.py
│   ├── status_text.py
│   └── app.py
├── deploy/        # Конфиги для деплоя
└── main.py        # Точка входа
```
