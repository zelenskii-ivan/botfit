# Bakery Bot — бот контроля кофейни/пекарни

Telegram-бот для напоминаний и контроля работы: молочка, выпечка, чеклисты открытия/закрытия.

📖 **Подробная инструкция:** [ИНСТРУКЦИЯ.md](ИНСТРУКЦИЯ.md)

## Функции

- **Молочка** (Вт/Чт/Сб): запрос фото + видео полки
- **Выпечка** (ежедневно): запрос фото витрины
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

API доступен на порту 8080: `GET /health`, `GET /status`

### Вариант 2: VPS + systemd

1. Создайте VPS в Timeweb Cloud
2. Скопируйте проект: `rsync -avz . user@server:~/bakery-bot/`
3. На сервере: создайте `.env`, настройте venv
4. Установите systemd unit: `sudo cp deploy/bakery-bot.service /etc/systemd/system/`
5. Отредактируйте пути в unit-файле
6. `sudo systemctl enable bakery-bot && sudo systemctl start bakery-bot`

### Health Check

- `GET /health` — для load balancer
- `GET /ready` — readiness probe
- `GET /status` — статус задач за день

## Команды бота

| Команда | Описание |
|---------|----------|
| /start | Справка |
| /id | Показать chat_id группы |
| /milk | Запросить молочку вручную |
| /bakery | Запросить выпечку вручную |
| /opening | Запросить чеклист открытия |
| /closing | Запросить чеклист закрытия |
| /status | Статус за сегодня |
| /memo | Памятка с обязательными работами |
| /opening_ok | Подтвердить чеклист открытия |
| /cash_ok | Подтвердить подсчёт наличных |
| /closing_ok | Подтвердить чеклист закрытия |

📦 **Деплой:** см. [DEPLOY.md](DEPLOY.md)

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
│   └── app.py
├── deploy/        # Конфиги для деплоя
└── main.py        # Точка входа
```
