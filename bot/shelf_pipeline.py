"""Vision → история → погода → рекомендация → рассылка."""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import BAKERY_RUN_SHELF_AI, GROUP_ID, MANAGER_CHAT_ID, OPENAI_API_KEY
from bot.shelf_period import is_shelf_season_active
from bot.shelf_recommendation import generate_recommendation
from bot.shelf_vision import analyze_shelf_image_bytes
from bot.state import clear_await, day_key, get_task, save_shelf_persist, shelf
from bot.weather import get_tomorrow_weather_cached

log = logging.getLogger(__name__)

_REMAINDER_SCORE = {"много": 3, "немного": 2, "почти нет": 1, "пусто": 0}


def _remainder_to_leftover_int(remainder: str) -> int:
    r = remainder.lower().strip()
    return _REMAINDER_SCORE.get(r, 2)


def _estimate_sold(name: str, leftover_now: int, sales_history: dict, today: str) -> int:
    try:
        prev_d = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=1)).date()
        prev_key = prev_d.strftime("%Y-%m-%d")
    except ValueError:
        return 0
    prev_rows = sales_history.get(prev_key, [])
    for row in prev_rows:
        if str(row.get("name", "")).lower() == name.lower():
            pl = int(row.get("leftover", 0))
            return max(0, pl - leftover_now)
    return 0


def _append_sales_history(items: list[dict[str, Any]]) -> None:
    today = day_key()
    rows: list[dict[str, Any]] = []
    hist = shelf.setdefault("sales_history", {})
    for it in items:
        name = it.get("name", "")
        rem = it.get("remainder", "немного")
        lo = _remainder_to_leftover_int(str(rem))
        sold = _estimate_sold(name, lo, hist, today)
        rows.append({"name": name, "sold": sold, "leftover": lo})
    hist[today] = rows
    save_shelf_persist()


async def run_shelf_pipeline_after_bakery_if_enabled(message: Message) -> None:
    """Если в .env включено — тот же сценарий полки по фото витрины выпечки."""
    if not BAKERY_RUN_SHELF_AI:
        return
    if not OPENAI_API_KEY:
        log.info("BAKERY_RUN_SHELF_AI: пропуск — нет OPENAI_API_KEY")
        return
    if not is_shelf_season_active():
        log.info("BAKERY_RUN_SHELF_AI: пропуск — вне сезона полки")
        return
    await download_and_process_shelf(message)


async def download_and_process_shelf(message: Message) -> None:
    if message.photo:
        buf = await message.bot.download(message.photo[-1])
        if buf is None:
            await message.reply("Не удалось скачать фото.")
            return
        data = buf.read()
        mime = "image/jpeg"
    elif message.document and message.document.mime_type and message.document.mime_type.startswith("image/"):
        buf = await message.bot.download(message.document)
        if buf is None:
            await message.reply("Не удалось скачать файл.")
            return
        data = buf.read()
        mime = message.document.mime_type
    else:
        await message.reply("Пришлите <b>фото</b> полки или файл-картинку.")
        return
    await process_shelf_photo_message(message, data, mime)


async def process_shelf_photo_message(message: Message, image_bytes: bytes, mime: str) -> None:
    if not is_shelf_season_active():
        await message.reply("Модуль полки активен с <b>27.04</b> по <b>20.05.2026</b>.")
        clear_await()
        return

    dk = day_key()
    await message.reply("⏳ Анализирую фото полки…")

    try:
        items = await analyze_shelf_image_bytes(image_bytes, mime=mime)
    except Exception as e:
        log.exception("shelf vision: %s", e)
        await message.reply(f"Не удалось разобрать фото: {e}")
        return

    shelf["today_remainders"] = {"date": dk, "items": items}
    _append_sales_history(items)

    try:
        weather = await get_tomorrow_weather_cached()
    except Exception as e:
        log.warning("weather: %s", e)
        weather = {"date": "", "description": "нет данных", "temp_min": None, "temp_max": None}

    try:
        text = await generate_recommendation(items, shelf.get("sales_history", {}), weather)
    except Exception as e:
        log.exception("recommendation: %s", e)
        await message.reply(f"Ошибка генерации рекомендации: {e}")
        clear_await()
        return

    st = get_task("shelf")
    st["photo"] = True
    st["analysis_done"] = True
    st["status"] = "done"

    shelf["recommendation_accepted"] = False
    tomorrow = (date.today() + timedelta(days=1)).strftime("%d.%m.%Y")
    wdesc = weather.get("description", "—")
    if weather.get("temp_min") is not None and weather.get("temp_max") is not None:
        wline = f"{wdesc}, {weather['temp_min']:.0f}…{weather['temp_max']:.0f} °C"
    else:
        wline = str(wdesc)

    body = (
        f"📊 <b>Рекомендация на завтра ({tomorrow})</b>\n"
        f"🌤 Погода: {wline}\n\n"
        f"{text}"
    )

    shelf["last_recommendation"] = {
        "date": dk,
        "text": text,
        "weather_line": wline,
        "full_html": body,
    }
    save_shelf_persist()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✅ Принято", callback_data="cb_shelf_accept")]],
    )

    bot = message.bot
    seen: set[int] = set()
    for cid in (MANAGER_CHAT_ID, GROUP_ID):
        if cid in seen:
            continue
        seen.add(cid)
        try:
            await bot.send_message(cid, body, reply_markup=kb)
        except Exception as e:
            log.warning("send shelf report to %s: %s", cid, e)

    await message.reply("✅ Отчёт сформирован и отправлен менеджеру и в группу.")
    clear_await()
