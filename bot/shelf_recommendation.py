"""Рекомендация выкладки: Claude или GPT-4o."""
from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from typing import Any

from bot.config import (
    ANTHROPIC_API_KEY,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    SHELF_RECOMMEND_ANTHROPIC_MODEL,
    SHELF_RECOMMEND_OPENAI_MODEL,
)

log = logging.getLogger(__name__)


def _history_for_prompt(sales_history: dict[str, list]) -> list[dict[str, Any]]:
    today = date.today()
    wd_tomorrow = (today + timedelta(days=1)).weekday()
    out: list[dict[str, Any]] = []
    for i in range(14):
        d = today - timedelta(days=i)
        key = d.strftime("%Y-%m-%d")
        if key not in sales_history:
            continue
        rows = sales_history[key]
        out.append(
            {
                "date": key,
                "weekday": d.weekday(),
                "same_weekday_as_tomorrow": d.weekday() == wd_tomorrow,
                "rows": rows,
            }
        )
    return out


def _build_user_prompt(remainders: list[dict], sales_history: dict, weather: dict[str, Any]) -> str:
    remainders_json = json.dumps(remainders, ensure_ascii=False)
    history_json = json.dumps(_history_for_prompt(sales_history), ensure_ascii=False)
    weather_json = json.dumps(weather, ensure_ascii=False)
    return (
        "Ты аналитик пекарни-кофейни. На основе данных ниже составь рекомендацию на завтра "
        "в трёх разделах:\n"
        "1. ВЫСТАВИТЬ ИЗ ОСТАТКОВ — позиции, которые есть на полке и можно выставить.\n"
        "2. ВЫПЕЧЬ — позиции, которых нет или мало, и которые хорошо продаются в похожие дни "
        "с учётом погоды (приоритет — строки истории с same_weekday_as_tomorrow=true).\n"
        "3. НЕ ПЕЧЬ / НЕ СТАВИТЬ — позиции, которые плохо продаются в похожую погоду или которых и так много осталось.\n"
        "Ответь кратко, по-русски, списками с эмодзи.\n\n"
        f"Данные:\nОстатки сегодня (Vision): {remainders_json}\n\n"
        f"История продаж (14 дней): {history_json}\n\n"
        f"Погода на завтра: {weather_json}"
    )


async def generate_recommendation(
    remainders: list[dict[str, Any]],
    sales_history: dict[str, list],
    weather: dict[str, Any],
) -> str:
    prompt = _build_user_prompt(remainders, sales_history, weather)

    if ANTHROPIC_API_KEY:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        msg = await client.messages.create(
            model=SHELF_RECOMMEND_ANTHROPIC_MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        parts: list[str] = []
        for block in msg.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        text = "".join(parts).strip()
        if text:
            return text

    if OPENAI_API_KEY:
        from openai import AsyncOpenAI

        kw: dict = {"api_key": OPENAI_API_KEY}
        if OPENAI_BASE_URL:
            kw["base_url"] = OPENAI_BASE_URL
        client = AsyncOpenAI(**kw)
        resp = await client.chat.completions.create(
            model=SHELF_RECOMMEND_OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.4,
        )
        t = (resp.choices[0].message.content or "").strip()
        if t:
            return t

    raise RuntimeError("Нужен ANTHROPIC_API_KEY или OPENAI_API_KEY для рекомендации полки")
