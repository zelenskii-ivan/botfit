"""Логика задач: запросы, напоминания, эскалация."""
import logging
from datetime import datetime, timedelta
from typing import Optional

from aiogram import Bot

from bot.config import (
    GROUP_ID,
    REMIND_AFTER_MIN,
    ESCALATE_AFTER_MIN,
    MILK_HOUR,
    MILK_MIN,
    BAKERY_HOUR,
    BAKERY_MIN,
    FREEZER_HOUR,
    FREEZER_MIN,
    OPENING_HOUR,
    OPENING_MIN,
    CASH_HOUR,
    CASH_MIN,
    CLOSING_HOUR,
    CLOSING_MIN,
    MEMO_HOUR_1,
    MEMO_MIN_1,
    MEMO_HOUR_2,
    MEMO_MIN_2,
    SANITARY_ENABLED,
    SANITARY_HOUR,
    SANITARY_MIN,
    EQUIPMENT_ENABLED,
    EQUIPMENT_HOUR,
    EQUIPMENT_MIN,
)
from bot.state import day_key, get_task, is_done, set_await

log = logging.getLogger(__name__)


def _schedule_reminders(bot: Bot, scheduler, task: str) -> None:
    """Напоминание и эскалация; при повторном запросе той же задачи старые даты заменяются."""
    now = datetime.now()
    scheduler.add_job(
        remind_if_needed,
        "date",
        run_date=now + timedelta(minutes=REMIND_AFTER_MIN),
        args=[bot, task],
        id=f"remind_{task}",
        replace_existing=True,
    )
    scheduler.add_job(
        escalate_if_needed,
        "date",
        run_date=now + timedelta(minutes=ESCALATE_AFTER_MIN),
        args=[bot, task],
        id=f"escalate_{task}",
        replace_existing=True,
    )


def _task_chat_id(task: str) -> int:
    """Чат, куда отправлять напоминания по задаче (откуда был запрос)."""
    st = get_task(task)
    return st.get("chat_id") or GROUP_ID


def _task_thread_id(task: str) -> Optional[int]:
    """Топик (если есть) для напоминаний."""
    st = get_task(task)
    return st.get("message_thread_id")


async def request_milk(bot: Bot, scheduler, chat_id: Optional[int] = None, message_thread_id: Optional[int] = None) -> None:
    """Вт/Чт/Сб: запрос фото + видео молочки."""
    cid = chat_id or GROUP_ID
    st = get_task("milk")
    st["status"] = "waiting"
    st["chat_id"] = cid
    st["message_thread_id"] = message_thread_id
    text = "🧊 <b>МОЛОЧКА</b>\nПришли <b>ФОТО полки с молочкой</b> (общий план)."
    log.info("request_milk: sending to chat_id=%s, thread_id=%s", cid, message_thread_id)
    kwargs = {"message_thread_id": message_thread_id} if message_thread_id else {}
    await bot.send_message(cid, text, **kwargs)
    set_await("milk", "photo", ESCALATE_AFTER_MIN, cid)

    _schedule_reminders(bot, scheduler, "milk")


async def request_bakery(bot: Bot, scheduler, chat_id: Optional[int] = None, message_thread_id: Optional[int] = None) -> None:
    """Каждый день: запрос фото выпечки."""
    cid = chat_id or GROUP_ID
    st = get_task("bakery")
    st["status"] = "waiting"
    st["chat_id"] = cid
    st["message_thread_id"] = message_thread_id
    text = "🥐 <b>ВЫПЕЧКА</b>\nПришли <b>ФОТО витрины с выпечкой</b> (общий план)."
    log.info("request_bakery: sending to chat_id=%s, thread_id=%s", cid, message_thread_id)
    kwargs = {"message_thread_id": message_thread_id} if message_thread_id else {}
    await bot.send_message(cid, text, **kwargs)
    set_await("bakery", "photo_only", ESCALATE_AFTER_MIN, cid)

    _schedule_reminders(bot, scheduler, "bakery")


async def request_freezer(bot: Bot, scheduler, chat_id: Optional[int] = None, message_thread_id: Optional[int] = None) -> None:
    """Ежедневно: запрос фото заморозки (пельмени, вареники, котлеты, голубцы и т.д.)."""
    cid = chat_id or GROUP_ID
    st = get_task("freezer")
    st["status"] = "waiting"
    st["chat_id"] = cid
    st["message_thread_id"] = message_thread_id
    text = (
        "❄️ <b>ЗАМОРОЗКА</b>\n"
        "Пришли <b>ФОТО витрины/морозилки</b> с заморозкой "
        "(пельмени, вареники, котлеты, голубцы и т.д.) — общий план."
    )
    log.info("request_freezer: sending to chat_id=%s, thread_id=%s", cid, message_thread_id)
    kwargs = {"message_thread_id": message_thread_id} if message_thread_id else {}
    await bot.send_message(cid, text, **kwargs)
    set_await("freezer", "photo_only", ESCALATE_AFTER_MIN, cid)

    _schedule_reminders(bot, scheduler, "freezer")


async def request_opening(bot: Bot, scheduler, chat_id: int = None) -> None:
    """Ежедневно: чеклист открытия."""
    cid = chat_id or GROUP_ID
    st = get_task("opening")
    st["status"] = "waiting"
    st["chat_id"] = cid
    st["checklist_done"] = False
    await bot.send_message(
        cid,
        "🌅 <b>ОТКРЫТИЕ</b>\nПодтвердите чеклист открытия:\n"
        "• Уборка зала\n• Проверка оборудования\n• Выкладка выпечки\n• Готовность кофемашины\n\n"
        "Ответьте /opening_ok когда всё готово.",
    )

    _schedule_reminders(bot, scheduler, "opening")


async def request_cash(bot: Bot, scheduler, chat_id: int = None) -> None:
    """Ежедневно 20:00: подсчёт наличных в кассе."""
    cid = chat_id or GROUP_ID
    st = get_task("cash")
    st["status"] = "waiting"
    st["chat_id"] = cid
    st["checklist_done"] = False
    await bot.send_message(
        cid,
        "💰 <b>ПОДСЧЁТ НАЛИЧНЫХ В КАССЕ</b>\n"
        "Проверьте и пересчитайте наличные в кассе.\n\n"
        "Ответьте /cash_ok когда подсчёт выполнен.",
    )

    _schedule_reminders(bot, scheduler, "cash")


async def request_closing(bot: Bot, scheduler, chat_id: int = None) -> None:
    """Ежедневно: чеклист закрытия."""
    cid = chat_id or GROUP_ID
    st = get_task("closing")
    st["status"] = "waiting"
    st["chat_id"] = cid
    st["checklist_done"] = False
    await bot.send_message(
        cid,
        "🌙 <b>ЗАКРЫТИЕ</b>\nПодтвердите чеклист закрытия:\n"
        "• Уборка зала\n• Выключение оборудования\n• Учёт выручки\n• Закрытие смены\n\n"
        "Ответьте /closing_ok когда всё готово.",
    )

    _schedule_reminders(bot, scheduler, "closing")


async def request_sanitary(bot: Bot, scheduler, chat_id: int = None) -> None:
    """Ежедневно: санитария и уборка по регламенту."""
    cid = chat_id or GROUP_ID
    st = get_task("sanitary")
    st["status"] = "waiting"
    st["chat_id"] = cid
    st["checklist_done"] = False
    await bot.send_message(
        cid,
        "🧹 <b>САНИТАРИЯ И УБОРКА</b>\n"
        "Подтвердите по регламенту:\n"
        "• Уборка зала и столиков\n• Санузел и зона мытья посуды\n• Вынос мусора\n\n"
        "Ответьте /sanitary_ok или кнопкой «Санитария ОК», когда всё сделано.",
    )
    _schedule_reminders(bot, scheduler, "sanitary")


async def request_equipment(bot: Bot, scheduler, chat_id: int = None) -> None:
    """Ежедневно: проверка оборудования."""
    cid = chat_id or GROUP_ID
    st = get_task("equipment")
    st["status"] = "waiting"
    st["chat_id"] = cid
    st["checklist_done"] = False
    await bot.send_message(
        cid,
        "🔧 <b>ПРОВЕРКА ОБОРУДОВАНИЯ</b>\n"
        "Подтвердите осмотр:\n"
        "• Кофемашина (вода, отходы, ошибки на дисплее)\n"
        "• Холодильники / морозилка (закрыты, без постороннего шума)\n"
        "• Освещение и вытяжка\n\n"
        "Ответьте /equipment_ok или кнопкой «Оборудование ОК», если всё в порядке.",
    )
    _schedule_reminders(bot, scheduler, "equipment")


async def remind_if_needed(bot: Bot, task: str) -> None:
    """Напоминание, если задача не выполнена."""
    if is_done(task):
        return

    cid = _task_chat_id(task)
    thread_id = _task_thread_id(task)
    kwargs = {"message_thread_id": thread_id} if thread_id else {}

    if task == "milk":
        st = get_task("milk")
        if st["photo"] and not st["video"]:
            await bot.send_message(cid, "⚠️ Напоминание: по <b>молочке</b> ещё нет <b>ВИДЕО</b>.", **kwargs)
        else:
            await bot.send_message(cid, "⚠️ Напоминание: по <b>молочке</b> нет отчёта. Нужны <b>ФОТО + ВИДЕО</b>.", **kwargs)
        return

    if task == "bakery":
        await bot.send_message(cid, "⚠️ Напоминание: по <b>выпечке</b> ещё нет <b>ФОТО витрины</b>.", **kwargs)
        return

    if task == "freezer":
        await bot.send_message(cid, "⚠️ Напоминание: по <b>заморозке</b> ещё нет <b>ФОТО витрины</b>.", **kwargs)
        return

    if task == "opening":
        await bot.send_message(cid, "⚠️ Напоминание: не подтверждён <b>чеклист открытия</b>. Ответьте /opening_ok", **kwargs)
        return

    if task == "closing":
        await bot.send_message(cid, "⚠️ Напоминание: не подтверждён <b>чеклист закрытия</b>. Ответьте /closing_ok", **kwargs)
        return

    if task == "cash":
        await bot.send_message(cid, "⚠️ Напоминание: не подтверждён <b>подсчёт наличных в кассе</b>. Ответьте /cash_ok", **kwargs)
        return

    if task == "sanitary":
        await bot.send_message(cid, "⚠️ Напоминание: не подтверждена <b>санитария и уборка</b>. Ответьте /sanitary_ok", **kwargs)
        return

    if task == "equipment":
        await bot.send_message(cid, "⚠️ Напоминание: не подтверждена <b>проверка оборудования</b>. Ответьте /equipment_ok", **kwargs)
        return


async def escalate_if_needed(bot: Bot, task: str) -> None:
    """Эскалация: задача не сдана."""
    if is_done(task):
        return

    d = day_key()
    cid = _task_chat_id(task)
    thread_id = _task_thread_id(task)
    kwargs = {"message_thread_id": thread_id} if thread_id else {}

    if task == "milk":
        st = get_task("milk")
        missing = []
        if not st["photo"]:
            missing.append("ФОТО")
        if not st["video"]:
            missing.append("ВИДЕО")
        await bot.send_message(cid, f"🚨 <b>НЕ СДАНО:</b> МОЛОЧКА за {d}. Нет: {', '.join(missing)}.", **kwargs)
        return

    if task == "bakery":
        await bot.send_message(cid, f"🚨 <b>НЕ СДАНО:</b> ВЫПЕЧКА за {d}. Нет: ФОТО витрины.", **kwargs)
        return

    if task == "freezer":
        await bot.send_message(cid, f"🚨 <b>НЕ СДАНО:</b> ЗАМОРОЗКА за {d}. Нет: ФОТО витрины.", **kwargs)
        return

    if task == "opening":
        await bot.send_message(cid, f"🚨 <b>НЕ СДАНО:</b> Чеклист ОТКРЫТИЯ за {d}.", **kwargs)
        return

    if task == "closing":
        await bot.send_message(cid, f"🚨 <b>НЕ СДАНО:</b> Чеклист ЗАКРЫТИЯ за {d}.", **kwargs)
        return

    if task == "cash":
        await bot.send_message(cid, f"🚨 <b>НЕ СДАНО:</b> Подсчёт наличных в кассе за {d}.", **kwargs)
        return

    if task == "sanitary":
        await bot.send_message(cid, f"🚨 <b>НЕ СДАНО:</b> Санитария и уборка за {d}.", **kwargs)
        return

    if task == "equipment":
        await bot.send_message(cid, f"🚨 <b>НЕ СДАНО:</b> Проверка оборудования за {d}.", **kwargs)
        return


async def send_memo(bot: Bot) -> None:
    """Отправить памятку с обязательными работами в группу (2 раза в день)."""
    from bot.memo import MEMO_TEXT
    await bot.send_message(GROUP_ID, "⏰ <b>Напоминание: обязательные работы</b>\n\n" + MEMO_TEXT)


def get_schedule_config() -> dict:
    """Конфиг расписания для scheduler."""
    return {
        "milk": {"day_of_week": "tue,thu,sat", "hour": MILK_HOUR, "minute": MILK_MIN},
        "bakery": {"hour": BAKERY_HOUR, "minute": BAKERY_MIN},
        "freezer": {"hour": FREEZER_HOUR, "minute": FREEZER_MIN},
        "opening": {"hour": OPENING_HOUR, "minute": OPENING_MIN},
        "cash": {"hour": CASH_HOUR, "minute": CASH_MIN},
        "closing": {"hour": CLOSING_HOUR, "minute": CLOSING_MIN},
        "memo_1": {"hour": MEMO_HOUR_1, "minute": MEMO_MIN_1},
        "memo_2": {"hour": MEMO_HOUR_2, "minute": MEMO_MIN_2},
        "sanitary": {
            "enabled": SANITARY_ENABLED,
            "hour": SANITARY_HOUR,
            "minute": SANITARY_MIN,
        },
        "equipment": {
            "enabled": EQUIPMENT_ENABLED,
            "hour": EQUIPMENT_HOUR,
            "minute": EQUIPMENT_MIN,
        },
    }
