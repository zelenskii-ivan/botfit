"""MAX command and content handlers."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Awaitable, Callable

from maxapi.types import Command, MessageCreated

from bot.config import ESCALATE_AFTER_MIN, MAX_GROUP_ID
from bot.memo import MEMO_TEXT
from bot.start_message import START_MESSAGE
from bot.state import clear_await, day_key, get_awaiting, get_task, set_await
from bot.status_text import format_day_status_html
from bot.tasks import (
    request_bakery,
    request_cash,
    request_closing,
    request_freezer,
    request_milk,
    request_opening,
    request_shelf_photo,
)
from bot_max.adapter import MaxBotAdapter, html_to_max_text
from bot_max.events import chat_id_from_event, has_image, has_video, text_from_event

log = logging.getLogger(__name__)


async def answer(event: MessageCreated, text: str) -> Any:
    return await event.message.answer(html_to_max_text(text))


def _chat_id(event: MessageCreated) -> int:
    cid = chat_id_from_event(event)
    if cid is None:
        raise RuntimeError("Не удалось определить MAX chat_id")
    return cid


def _register_command(dp: Any, name: str, handler: Callable[[MessageCreated], Awaitable[Any]]) -> None:
    dp.message_created(Command(name))(handler)


def register_handlers(dp: Any, bot: MaxBotAdapter, scheduler: Any) -> None:
    """Register MAX handlers on a Dispatcher."""

    async def start(event: MessageCreated) -> None:
        await answer(event, START_MESSAGE)

    async def memo(event: MessageCreated) -> None:
        await answer(event, MEMO_TEXT)

    async def status(event: MessageCreated) -> None:
        await answer(event, format_day_status_html(day_key()))

    async def ping(event: MessageCreated) -> None:
        cid = _chat_id(event)
        await answer(event, f"🏓 Pong! MAX chat_id={cid}\nЦелевая группа: {'да' if cid == MAX_GROUP_ID else 'нет'}")

    async def chat_id(event: MessageCreated) -> None:
        cid = _chat_id(event)
        await answer(event, f"MAX chat_id: {cid}\nЦелевая группа: {'✅ да' if cid == MAX_GROUP_ID else '❌ нет'}")

    async def milk(event: MessageCreated) -> None:
        await request_milk(bot, scheduler, _chat_id(event))

    async def bakery(event: MessageCreated) -> None:
        await request_bakery(bot, scheduler, _chat_id(event))

    async def freezer(event: MessageCreated) -> None:
        await request_freezer(bot, scheduler, _chat_id(event))

    async def opening(event: MessageCreated) -> None:
        await request_opening(bot, scheduler, _chat_id(event))

    async def cash(event: MessageCreated) -> None:
        await request_cash(bot, scheduler, _chat_id(event))

    async def closing(event: MessageCreated) -> None:
        await request_closing(bot, scheduler, _chat_id(event))

    async def opening_ok(event: MessageCreated) -> None:
        st = get_task("opening")
        st["checklist_done"] = True
        st["status"] = "done"
        await answer(event, "✅ <b>ОТКРЫТИЕ</b>: чеклист подтверждён.")

    async def cash_ok(event: MessageCreated) -> None:
        st = get_task("cash")
        st["checklist_done"] = True
        st["status"] = "done"
        await answer(event, "✅ <b>ПОДСЧЁТ НАЛИЧНЫХ</b>: подтверждён.")

    async def closing_ok(event: MessageCreated) -> None:
        st = get_task("closing")
        st["checklist_done"] = True
        st["status"] = "done"
        await answer(event, "✅ <b>ЗАКРЫТИЕ</b>: чеклист подтверждён.")

    async def shelf(event: MessageCreated) -> None:
        from bot.shelf_period import is_shelf_season_active

        if not is_shelf_season_active():
            await answer(event, "Модуль полки активен с <b>27.04</b> по <b>20.05.2026</b>.")
            return
        await request_shelf_photo(bot, scheduler, _chat_id(event))

    async def shelf_report(event: MessageCreated) -> None:
        from bot.state import shelf as shelf_state

        lr = shelf_state.get("last_recommendation")
        if not lr or not lr.get("full_html"):
            await answer(event, "Пока нет сохранённой рекомендации по полке.")
            return
        await answer(event, lr["full_html"])

    async def shelf_history(event: MessageCreated) -> None:
        from datetime import date, timedelta

        from bot.state import shelf as shelf_state

        hist = shelf_state.get("sales_history", {})
        lines: list[str] = []
        for i in range(7):
            d = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            rows = hist.get(d)
            if not rows:
                continue
            parts = [f"{r['name']} (прод.≈{r['sold']}, ост.{r['leftover']})" for r in rows[:10]]
            lines.append(f"• <b>{d}</b>: " + ", ".join(parts))
        await answer(event, "📈 <b>История полки (7 дней)</b>\n" + "\n".join(lines) if lines else "За последние 7 дней нет записей истории полки.")

    for name, handler in {
        "start": start,
        "help": start,
        "memo": memo,
        "status": status,
        "ping": ping,
        "id": chat_id,
        "milk": milk,
        "bakery": bakery,
        "freezer": freezer,
        "opening": opening,
        "cash": cash,
        "closing": closing,
        "opening_ok": opening_ok,
        "cash_ok": cash_ok,
        "closing_ok": closing_ok,
        "shelf": shelf,
        "shelf_report": shelf_report,
        "shelf_history": shelf_history,
    }.items():
        _register_command(dp, name, handler)

    @dp.message_created()
    async def content(event: MessageCreated) -> None:
        text = text_from_event(event)
        if text.startswith("/"):
            return
        if text == "📌 Статус":
            await status(event)
            return
        if text == "📋 Памятка":
            await memo(event)
            return
        if text == "🧊 Молочка":
            await milk(event)
            return
        if text == "🥐 Выпечка":
            await bakery(event)
            return
        if text == "❄️ Заморозка":
            await freezer(event)
            return
        if text == "🌅 Открытие ОК":
            await opening_ok(event)
            return
        if text == "💰 Касса ОК":
            await cash_ok(event)
            return
        if text == "🌙 Закрытие ОК":
            await closing_ok(event)
            return

        awaiting = get_awaiting()
        if not awaiting or awaiting["until"] < datetime.now():
            return
        cid = _chat_id(event)
        if cid != awaiting.get("chat_id", MAX_GROUP_ID):
            return

        task = awaiting["task"]
        need = awaiting["need"]
        if has_image(event):
            await _handle_image(event, task, need, cid)
            return
        if has_video(event):
            await _handle_video(event, task, need)


async def _handle_image(event: MessageCreated, task: str, need: str, chat_id: int) -> None:
    if need not in ("photo", "photo_only"):
        await answer(event, "Сейчас бот ждёт <b>ВИДЕО</b>, а не фото.")
        return

    if task == "shelf":
        st = get_task("shelf")
        st["photo"] = True
        st["analysis_done"] = False
        st["status"] = "done"
        clear_await()
        await answer(event, "✅ Фото полки принято. ИИ-анализ для MAX будет подключён в следующем релизе.")
        return

    st = get_task(task)
    st["photo"] = True
    if task == "milk":
        await answer(event, "✅ <b>МОЛОЧКА</b>: фото принято. Теперь пришлите <b>ВИДЕО</b> полки с молочкой.")
        set_await("milk", "video", ESCALATE_AFTER_MIN, chat_id)
        return
    if task == "bakery":
        st["status"] = "done"
        clear_await()
        await answer(event, "✅ <b>ВЫПЕЧКА</b>: фото витрины принято.")
        return
    if task == "freezer":
        st["status"] = "done"
        clear_await()
        await answer(event, "✅ <b>ЗАМОРОЗКА</b>: фото витрины принято.")


async def _handle_video(event: MessageCreated, task: str, need: str) -> None:
    if need != "video":
        await answer(event, "Сейчас бот ждёт <b>ФОТО</b>, а не видео.")
        return
    st = get_task(task)
    st["video"] = True
    if task == "milk":
        st["status"] = "done"
        clear_await()
        await answer(event, "✅ <b>МОЛОЧКА</b>: видео принято. Отчёт закрыт.")

