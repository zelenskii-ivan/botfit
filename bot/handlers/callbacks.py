"""Обработчики нажатий на inline-кнопки."""
import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.config import GROUP_ID
from bot.state import day_key, get_task
from bot.status_text import format_day_status_html
from bot.keyboards import main_keyboard, memo_keyboard
from bot.memo import MEMO_TEXT
from bot.tasks import request_milk, request_bakery, request_freezer

log = logging.getLogger(__name__)
router = Router()


def _get_bot_and_scheduler():
    from bot.app import bot, scheduler
    return bot, scheduler


@router.callback_query(F.data == "cb_test")
async def cb_test(callback: CallbackQuery):
    await callback.answer("Кнопка работает! ✅")


@router.callback_query(F.data == "cb_status")
async def cb_status(callback: CallbackQuery):
    await callback.answer()
    text = format_day_status_html(day_key())
    await callback.message.edit_text(text, reply_markup=main_keyboard())


@router.callback_query(F.data == "cb_memo")
async def cb_memo(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(MEMO_TEXT, reply_markup=memo_keyboard())


@router.callback_query(F.data == "cb_back")
async def cb_back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Я бот контроля кофейни (работаю <b>в группе</b>).\n\nВыберите действие:",
        reply_markup=main_keyboard(),
    )


def _chat_context(msg):
    """Извлечь chat_id и message_thread_id (для топиков) из сообщения."""
    chat_id = msg.chat.id
    thread_id = getattr(msg, "message_thread_id", None)
    return chat_id, thread_id


@router.callback_query(F.data == "cb_milk")
async def cb_milk(callback: CallbackQuery):
    await callback.answer()
    if not callback.message:
        log.warning("cb_milk: callback.message is None")
        return
    chat_id, thread_id = _chat_context(callback.message)
    log.info("cb_milk: chat_id=%s, thread_id=%s (GROUP_ID=%s)", chat_id, thread_id, GROUP_ID)
    bot, scheduler = _get_bot_and_scheduler()
    await request_milk(bot, scheduler, chat_id=chat_id, message_thread_id=thread_id)


@router.callback_query(F.data == "cb_bakery")
async def cb_bakery(callback: CallbackQuery):
    await callback.answer()
    if not callback.message:
        log.warning("cb_bakery: callback.message is None")
        return
    chat_id, thread_id = _chat_context(callback.message)
    log.info("cb_bakery: chat_id=%s, thread_id=%s (GROUP_ID=%s)", chat_id, thread_id, GROUP_ID)
    bot, scheduler = _get_bot_and_scheduler()
    await request_bakery(bot, scheduler, chat_id=chat_id, message_thread_id=thread_id)


@router.callback_query(F.data == "cb_freezer")
async def cb_freezer(callback: CallbackQuery):
    await callback.answer()
    if not callback.message:
        log.warning("cb_freezer: callback.message is None")
        return
    chat_id, thread_id = _chat_context(callback.message)
    log.info("cb_freezer: chat_id=%s, thread_id=%s (GROUP_ID=%s)", chat_id, thread_id, GROUP_ID)
    bot, scheduler = _get_bot_and_scheduler()
    await request_freezer(bot, scheduler, chat_id=chat_id, message_thread_id=thread_id)


@router.callback_query(F.data == "cb_opening_ok")
async def cb_opening_ok(callback: CallbackQuery):
    await callback.answer("Открытие подтверждено")
    st = get_task("opening")
    st["checklist_done"] = True
    st["status"] = "done"
    await callback.message.answer("✅ <b>ОТКРЫТИЕ</b>: чеклист подтверждён.")


@router.callback_query(F.data == "cb_cash_ok")
async def cb_cash_ok(callback: CallbackQuery):
    await callback.answer("Подсчёт подтверждён")
    st = get_task("cash")
    st["checklist_done"] = True
    st["status"] = "done"
    await callback.message.answer("✅ <b>ПОДСЧЁТ НАЛИЧНЫХ</b>: подтверждён.")


@router.callback_query(F.data == "cb_closing_ok")
async def cb_closing_ok(callback: CallbackQuery):
    await callback.answer("Закрытие подтверждено")
    st = get_task("closing")
    st["checklist_done"] = True
    st["status"] = "done"
    await callback.message.answer("✅ <b>ЗАКРЫТИЕ</b>: чеклист подтверждён.")
