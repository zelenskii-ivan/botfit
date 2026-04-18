#!/bin/bash
# Скрипт деплоя на Timeweb Cloud VPS
# Использование: ./deploy/deploy.sh user@your-server-ip

set -e
TARGET=${1:? "Usage: $0 user@server"}

echo "==> Деплой bakery-bot на $TARGET"

# Сборка и копирование
rsync -avz --exclude '.git' --exclude '__pycache__' --exclude 'venv' --exclude '.env' \
  . "$TARGET:~/bakery-bot/"

echo "==> Запуск на сервере..."
ssh "$TARGET" "cd ~/bakery-bot && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

echo "==> Перезапуск systemd (если настроен)..."
ssh "$TARGET" "sudo systemctl restart bakery-bot 2>/dev/null || echo 'Сервис не настроен. Запустите: python main.py'"

echo "==> Готово."
