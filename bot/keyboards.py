"""Клавиатуры."""
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📌 Статус", callback_data="cb_status"),
            InlineKeyboardButton(text="📋 Памятка", callback_data="cb_memo"),
        ],
        [
            InlineKeyboardButton(text="🧊 Молочка", callback_data="cb_milk"),
            InlineKeyboardButton(text="🥐 Выпечка", callback_data="cb_bakery"),
        ],
        [
            InlineKeyboardButton(text="❄️ Заморозка", callback_data="cb_freezer"),
        ],
        [
            InlineKeyboardButton(text="🌅 Открытие ОК", callback_data="cb_opening_ok"),
            InlineKeyboardButton(text="💰 Касса ОК", callback_data="cb_cash_ok"),
        ],
        [
            InlineKeyboardButton(text="🌙 Закрытие ОК", callback_data="cb_closing_ok"),
        ],
    ])


def memo_keyboard() -> InlineKeyboardMarkup:
    """Кнопка «Назад» под памяткой."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="cb_back")],
    ])


def reply_keyboard() -> ReplyKeyboardMarkup:
    """Постоянная клавиатура внизу экрана."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📌 Статус"), KeyboardButton(text="📋 Памятка")],
            [KeyboardButton(text="🧊 Молочка"), KeyboardButton(text="🥐 Выпечка")],
            [KeyboardButton(text="❄️ Заморозка")],
            [KeyboardButton(text="🌅 Открытие ОК"), KeyboardButton(text="💰 Касса ОК")],
            [KeyboardButton(text="🌙 Закрытие ОК")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
