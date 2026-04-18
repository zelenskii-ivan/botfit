# Деплой на Timeweb Cloud

## Что нужно для деплоя

### 1. Аккаунт Timeweb Cloud
- Зарегистрируйтесь на [timeweb.cloud](https://timeweb.cloud)
- Создайте VPS (Ubuntu 22.04 или новее) или используйте Docker

### 2. Данные для настройки
- **BOT_TOKEN** — токен от @BotFather
- **GROUP_ID** — ID группы (получить через /id в боте)
- Файл **.env** с переменными окружения

---

## Вариант A: Docker (рекомендуется)

### На VPS Timeweb:

```bash
# 1. Установите Docker (если нет)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Перелогиньтесь

# 2. Скопируйте проект на сервер
scp -r botrop/ user@ВАШ_IP:~/

# 3. На сервере
cd ~/botrop
# Создайте .env (скопируйте с локальной машины или создайте вручную)
nano .env   # BOT_TOKEN, GROUP_ID и др.

# 4. Запуск
docker compose up -d

# 5. Проверка
curl http://localhost:8080/health
docker compose logs -f bot
```

---

## Вариант B: Без Docker (systemd)

### На VPS Timeweb:

```bash
# 1. Подключитесь по SSH
ssh user@ВАШ_IP

# 2. Установите Python 3.11
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip

# 3. Скопируйте проект
scp -r botrop/ user@ВАШ_IP:~/bakery-bot/

# 4. На сервере
cd ~/bakery-bot
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Создайте .env
cp .env.example .env
nano .env   # Заполните BOT_TOKEN, GROUP_ID

# 6. Установите systemd
sudo cp deploy/bakery-bot.service /etc/systemd/system/
# Отредактируйте пути (User, WorkingDirectory) если логин не deploy
sudo nano /etc/systemd/system/bakery-bot.service

sudo systemctl daemon-reload
sudo systemctl enable bakery-bot
sudo systemctl start bakery-bot
sudo systemctl status bakery-bot

# 7. Логи
journalctl -u bakery-bot -f
```

---

## Содержимое .env

```
BOT_TOKEN=ваш_токен_от_botfather
GROUP_ID=-1005004718978

REMIND_AFTER_MIN=15
ESCALATE_AFTER_MIN=30

MILK_HOUR=13
MILK_MIN=0
BAKERY_HOUR=20
BAKERY_MIN=0
FREEZER_HOUR=20
FREEZER_MIN=5
OPENING_HOUR=7
OPENING_MIN=0
CASH_HOUR=20
CASH_MIN=0
CLOSING_HOUR=21
CLOSING_MIN=0

SANITARY_ENABLED=true
SANITARY_HOUR=14
SANITARY_MIN=0
EQUIPMENT_ENABLED=true
EQUIPMENT_HOUR=12
EQUIPMENT_MIN=0

AI_ENABLED=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

MEMO_HOUR_1=9
MEMO_MIN_1=0
MEMO_HOUR_2=15
MEMO_MIN_2=0

API_HOST=0.0.0.0
API_PORT=8080
RUN_API=true
```

---

## Быстрая копия проекта на сервер

```bash
# С вашего Mac (из папки с botrop)
rsync -avz --exclude '.git' --exclude 'venv' --exclude '__pycache__' \
  botrop/ user@IP_СЕРВЕРА:~/bakery-bot/
```

**Важно:** файл .env не копируется (в .gitignore). Создайте его на сервере вручную или добавьте `--include '.env'` в rsync.

---

## Проверка после деплоя

1. `curl -s http://ВАШ_IP:8080/health` — `{"status":"healthy",...}`
2. `curl -s http://ВАШ_IP:8080/version` — `{"service":"bakery-bot","version":"1.1.0",...}`
3. Напишите боту `/start` в Telegram — должен ответить
4. В группе отправьте `/id` — бот покажет chat_id
