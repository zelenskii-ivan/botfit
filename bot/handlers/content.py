"""Обработчики фото и видео."""
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message

from bot.config import GROUP_ID, ESCALATE_AFTER_MIN
from bot.state import get_task, get_awaiting, set_await, clear_await

router = Router()


@router.message(F.photo)
async def on_photo(message: Message):
    awaiting = get_awaiting()
    if not awaiting or awaiting["until"] < datetime.now():
        return
    chat_id = awaiting.get("chat_id", GROUP_ID)
    if message.chat.id != chat_id:
        return

    task = awaiting["task"]
    need = awaiting["need"]

    if need not in ("photo", "photo_only"):
        await message.reply("Сейчас бот ждёт <b>ВИДЕО</b>, а не фото.")
        return

    st = get_task(task)
    st["photo"] = True

    if task == "milk":
        await message.reply(
            "✅ <b>МОЛОЧКА</b>: фото принято. Теперь пришли <b>ВИДЕО</b> полки с молочкой (короткое, 5–10 сек)."
        )
        set_await("milk", "video", ESCALATE_AFTER_MIN, chat_id)
        return

    if task == "bakery":
        st["status"] = "done"
        await message.reply("✅ <b>ВЫПЕЧКА</b>: фото витрины принято.")
        clear_await()
        return

    if task == "freezer":
        st["status"] = "done"
        await message.reply("✅ <b>ЗАМОРОЗКА</b>: фото витрины принято.")
        clear_await()


@router.message(F.video)
@router.message(F.video_note)
async def on_video(message: Message):
    awaiting = get_awaiting()
    if not awaiting or awaiting["until"] < datetime.now():
        return
    chat_id = awaiting.get("chat_id", GROUP_ID)
    if message.chat.id != chat_id:
        return

    task = awaiting["task"]
    need = awaiting["need"]

    if need != "video":
        await message.reply("Сейчас бот ждёт <b>ФОТО</b>, а не видео.")
        return

    st = get_task(task)
    st["video"] = True

    if task == "milk":
        st["status"] = "done"
        await message.reply("✅ <b>МОЛОЧКА</b>: видео принято. Отчёт закрыт.")
        clear_await()
