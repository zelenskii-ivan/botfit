"""Обработчики команд."""
import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import GROUP_ID  # для /id и /ping
from bot.keyboards import main_keyboard, reply_keyboard

log = logging.getLogger(__name__)
from bot.state import day_key, get_task
from bot.status_text import format_day_status_html
from bot.tasks import (
    request_milk,
    request_bakery,
    request_freezer,
    request_opening,
    request_cash,
    request_closing,
    request_shelf_photo,
)

router = Router()


def _get_bot_and_scheduler():
    """Получить bot и scheduler из app (инжектируется при старте)."""
    from bot.app import bot, scheduler
    return bot, scheduler


@router.message(Command("start"))
async def start(message: Message):
    log.info("start from chat_id=%s", message.chat.id)
    from bot.start_message import START_MESSAGE
    markup = reply_keyboard() if message.chat.type == "private" else main_keyboard()
    await message.answer(START_MESSAGE, reply_markup=markup)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Краткая справка (дублирует /start для удобства)."""
    from bot.start_message import START_MESSAGE
    markup = reply_keyboard() if message.chat.type == "private" else main_keyboard()
    await message.answer(START_MESSAGE, reply_markup=markup)


@router.message(F.text == "📌 Статус")
async def btn_status(message: Message):
    """Обработка кнопки Статус."""
    await message.answer(format_day_status_html(day_key()))


@router.message(F.text == "📋 Памятка")
async def btn_memo(message: Message):
    """Обработка кнопки Памятка."""
    from bot.memo import MEMO_TEXT
    await message.answer(MEMO_TEXT)


@router.message(F.text == "🧊 Молочка")
async def btn_milk(message: Message):
    bot, scheduler = _get_bot_and_scheduler()
    await request_milk(bot, scheduler, message.chat.id)


@router.message(F.text == "🥐 Выпечка")
async def btn_bakery(message: Message):
    bot, scheduler = _get_bot_and_scheduler()
    await request_bakery(bot, scheduler, message.chat.id)


@router.message(F.text == "❄️ Заморозка")
async def btn_freezer(message: Message):
    bot, scheduler = _get_bot_and_scheduler()
    await request_freezer(bot, scheduler, message.chat.id)


@router.message(F.text == "🌅 Открытие ОК")
async def btn_opening_ok(message: Message):
    st = get_task("opening")
    st["checklist_done"] = True
    st["status"] = "done"
    await message.reply("✅ <b>ОТКРЫТИЕ</b>: чеклист подтверждён.")


@router.message(F.text == "💰 Касса ОК")
async def btn_cash_ok(message: Message):
    st = get_task("cash")
    st["checklist_done"] = True
    st["status"] = "done"
    await message.reply("✅ <b>ПОДСЧЁТ НАЛИЧНЫХ</b>: подтверждён.")


@router.message(F.text == "🌙 Закрытие ОК")
async def btn_closing_ok(message: Message):
    st = get_task("closing")
    st["checklist_done"] = True
    st["status"] = "done"
    await message.reply("✅ <b>ЗАКРЫТИЕ</b>: чеклист подтверждён.")


@router.message(Command("memo"))
async def cmd_memo(message: Message):
    """Памятка с обязательными работами."""
    from bot.memo import MEMO_TEXT
    from bot.keyboards import memo_keyboard
    await message.answer(MEMO_TEXT, reply_markup=memo_keyboard())


@router.message(Command("keyboard"))
async def cmd_keyboard(message: Message):
    """Тест: отправить сообщение с одной кнопкой."""
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Нажми меня", callback_data="cb_test")],
    ])
    await message.answer("Если видите кнопку ниже — клавиатура работает:", reply_markup=kb)


@router.message(Command("ping"))
async def cmd_ping(message: Message):
    """Отвечает в любом чате — для проверки работы бота."""
    log.info("ping from chat_id=%s", message.chat.id)
    in_group = message.chat.id == GROUP_ID
    await message.answer(f"🏓 Pong! chat_id=<code>{message.chat.id}</code>\nВ целевой группе: {'да' if in_group else 'нет'}")


@router.message(Command("id"))
async def cmd_id(message: Message):
    log.info("id from chat_id=%s", message.chat.id)
    in_target = message.chat.id == GROUP_ID
    text = f"chat_id: <code>{message.chat.id}</code>"
    if message.chat.type in ("group", "supergroup"):
        text += f"\n\nЦелевая группа: {'✅ да' if in_target else '❌ нет (GROUP_ID=' + str(GROUP_ID) + ')'}"
        if not in_target:
            text += "\n\nОбновите GROUP_ID в .env и перезапустите бота."
    await message.answer(text)


@router.message(Command("milk"))
async def cmd_milk(message: Message):
    bot, scheduler = _get_bot_and_scheduler()
    await request_milk(bot, scheduler, message.chat.id)


@router.message(Command("bakery"))
async def cmd_bakery(message: Message):
    bot, scheduler = _get_bot_and_scheduler()
    await request_bakery(bot, scheduler, message.chat.id)


@router.message(Command("freezer"))
async def cmd_freezer(message: Message):
    bot, scheduler = _get_bot_and_scheduler()
    await request_freezer(bot, scheduler, message.chat.id)


@router.message(Command("opening"))
async def cmd_opening(message: Message):
    bot, scheduler = _get_bot_and_scheduler()
    await request_opening(bot, scheduler, message.chat.id)


@router.message(Command("cash"))
async def cmd_cash(message: Message):
    bot, scheduler = _get_bot_and_scheduler()
    await request_cash(bot, scheduler, message.chat.id)


@router.message(Command("closing"))
async def cmd_closing(message: Message):
    bot, scheduler = _get_bot_and_scheduler()
    await request_closing(bot, scheduler, message.chat.id)


@router.message(Command("opening_ok"))
async def cmd_opening_ok(message: Message):
    st = get_task("opening")
    st["checklist_done"] = True
    st["status"] = "done"
    await message.reply("✅ <b>ОТКРЫТИЕ</b>: чеклист подтверждён.")


@router.message(Command("closing_ok"))
async def cmd_closing_ok(message: Message):
    st = get_task("closing")
    st["checklist_done"] = True
    st["status"] = "done"
    await message.reply("✅ <b>ЗАКРЫТИЕ</b>: чеклист подтверждён.")


@router.message(Command("cash_ok"))
async def cmd_cash_ok(message: Message):
    st = get_task("cash")
    st["checklist_done"] = True
    st["status"] = "done"
    await message.reply("✅ <b>ПОДСЧЁТ НАЛИЧНЫХ</b>: подтверждён.")


@router.message(Command("status"))
async def cmd_status(message: Message):
    await message.answer(format_day_status_html(day_key()))


@router.message(Command("shelf"))
async def cmd_shelf(message: Message):
    from bot.shelf_period import is_shelf_season_active

    if not is_shelf_season_active():
        await message.answer("Модуль полки активен с <b>27.04</b> по <b>20.05.2026</b>.")
        return
    bot, scheduler = _get_bot_and_scheduler()
    await request_shelf_photo(bot, scheduler, message.chat.id)


@router.message(Command("shelf_report"))
async def cmd_shelf_report(message: Message):
    from bot.state import shelf

    lr = shelf.get("last_recommendation")
    if not lr or not lr.get("full_html"):
        await message.answer("Пока нет сохранённой рекомендации по полке.")
        return
    await message.answer(lr["full_html"])


@router.message(Command("shelf_history"))
async def cmd_shelf_history(message: Message):
    from datetime import date, timedelta

    from bot.state import shelf

    hist = shelf.get("sales_history", {})
    lines: list[str] = []
    for i in range(7):
        d = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        rows = hist.get(d)
        if not rows:
            continue
        parts = [f"{r['name']} (прод.≈{r['sold']}, ост.{r['leftover']})" for r in rows[:10]]
        lines.append(f"• <b>{d}</b>: " + ", ".join(parts))
    if not lines:
        await message.answer("За последние 7 дней нет записей истории полки.")
        return
    await message.answer("📈 <b>История полки (7 дней)</b>\n" + "\n".join(lines))
