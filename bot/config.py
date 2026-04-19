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

# OpenAI (Vision + рекомендация при отсутствии Claude)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None

# После фото выпечки запускать тот же ИИ (Vision + рекомендация), что и для полки
BAKERY_RUN_SHELF_AI = os.getenv("BAKERY_RUN_SHELF_AI", "false").lower() == "true"

# Модуль полки (27.04–20.05.2026)
SHELF_ENABLED = os.getenv("SHELF_ENABLED", "false").lower() == "true"
SHELF_HOUR = int(os.getenv("SHELF_HOUR", "19"))
SHELF_MIN = int(os.getenv("SHELF_MIN", "30"))
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID", str(GROUP_ID)))


def _opt_float(name: str):
    v = os.getenv(name, "").strip()
    return float(v) if v else None


WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "").strip()
WEATHER_CITY = os.getenv("WEATHER_CITY", "Moscow")
WEATHER_LAT = _opt_float("WEATHER_LAT")
WEATHER_LON = _opt_float("WEATHER_LON")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
SHELF_RECOMMEND_ANTHROPIC_MODEL = os.getenv("SHELF_RECOMMEND_ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
SHELF_RECOMMEND_OPENAI_MODEL = os.getenv("SHELF_RECOMMEND_OPENAI_MODEL", "gpt-4o")

# API (для health check и мониторинга)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8080"))
