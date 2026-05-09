"""Inline keyboards for MAX messages."""
from __future__ import annotations

from maxapi.types.attachments.buttons import MessageButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder


def main_keyboard():
    """Buttons that send the same text commands handled by content()."""
    return (
        InlineKeyboardBuilder()
        .row(MessageButton(text="📌 Статус"))
        .row(MessageButton(text="📋 Памятка"))
        .row(MessageButton(text="🧊 Молочка"), MessageButton(text="🥐 Выпечка"))
        .row(MessageButton(text="❄️ Заморозка"))
        .row(MessageButton(text="🌅 Открытие ОК"), MessageButton(text="💰 Касса ОК"))
        .row(MessageButton(text="🌙 Закрытие ОК"))
        .as_markup()
    )


def memo_keyboard():
    """Compact keyboard for reminder messages."""
    return (
        InlineKeyboardBuilder()
        .row(MessageButton(text="📌 Статус"))
        .row(MessageButton(text="🌅 Открытие ОК"), MessageButton(text="💰 Касса ОК"))
        .row(MessageButton(text="🌙 Закрытие ОК"))
        .as_markup()
    )
