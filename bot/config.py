"""Конфигурация бота и расписания."""
import os

# Telegram
API_TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")
GROUP_ID = int(os.getenv("GROUP_ID", "-1001234567890"))

# Таймауты (минуты)
REMIND_AFTER_MIN = int(os.getenv("REMIND_AFTER_MIN", "15"))
ESCALATE_AFTER_MIN = int(os.getenv("ESCALATE_AFTER_MIN", "30"))

# Расписание молочки (Вт/Чт/Сб)
MILK_HOUR = int(os.getenv("MILK_HOUR", "13"))
MILK_MIN = int(os.getenv("MILK_MIN", "0"))

# Расписание выпечки (ежедневно)
BAKERY_HOUR = int(os.getenv("BAKERY_HOUR", "20"))
BAKERY_MIN = int(os.getenv("BAKERY_MIN", "0"))

# Расписание заморозки (ежедневно: пельмени, вареники, котлеты, голубцы)
FREEZER_HOUR = int(os.getenv("FREEZER_HOUR", "20"))
FREEZER_MIN = int(os.getenv("FREEZER_MIN", "5"))

# Расписание открытия (ежедневно, 7:00)
OPENING_HOUR = int(os.getenv("OPENING_HOUR", "7"))
OPENING_MIN = int(os.getenv("OPENING_MIN", "0"))

# Подсчёт наличных в кассе (ежедневно, 20:00)
CASH_HOUR = int(os.getenv("CASH_HOUR", "20"))
CASH_MIN = int(os.getenv("CASH_MIN", "0"))

# Расписание закрытия (ежедневно)
CLOSING_HOUR = int(os.getenv("CLOSING_HOUR", "21"))
CLOSING_MIN = int(os.getenv("CLOSING_MIN", "0"))

# Памятка 2 раза в день (обязательные работы)
MEMO_HOUR_1 = int(os.getenv("MEMO_HOUR_1", "9"))
MEMO_MIN_1 = int(os.getenv("MEMO_MIN_1", "0"))
MEMO_HOUR_2 = int(os.getenv("MEMO_HOUR_2", "15"))
MEMO_MIN_2 = int(os.getenv("MEMO_MIN_2", "0"))

# Регламент: санитария (ежедневный чеклист)
SANITARY_ENABLED = os.getenv("SANITARY_ENABLED", "true").lower() == "true"
SANITARY_HOUR = int(os.getenv("SANITARY_HOUR", "14"))
SANITARY_MIN = int(os.getenv("SANITARY_MIN", "0"))

# Регламент: проверка оборудования (ежедневно)
EQUIPMENT_ENABLED = os.getenv("EQUIPMENT_ENABLED", "true").lower() == "true"
EQUIPMENT_HOUR = int(os.getenv("EQUIPMENT_HOUR", "12"))
EQUIPMENT_MIN = int(os.getenv("EQUIPMENT_MIN", "0"))

# ИИ (OpenAI-совместимый API)
AI_ENABLED = os.getenv("AI_ENABLED", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None  # для прокси / Azure / др.

# API (для health check и мониторинга)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8080"))
