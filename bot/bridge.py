"""Text bridge between Telegram and MAX group chats."""
from __future__ import annotations

import logging
from typing import Any

from aiogram import Bot as TelegramBot
from aiogram.types import Message
from maxapi import Bot as MaxBot

from bot.config import (
    API_TOKEN,
    BRIDGE_ENABLED,
    MAX_BOT_TOKEN,
    MAX_BRIDGE_CHAT_ID,
    TELEGRAM_BRIDGE_CHAT_ID,
)
from bot_max.events import chat_id_from_event, dig, text_from_event

log = logging.getLogger(__name__)

_BRIDGE_PREFIXES = ("TG | ", "MAX | ")


def _is_bridge_text(text: str) -> bool:
    return text.startswith(_BRIDGE_PREFIXES)


def _is_command_text(text: str) -> bool:
    parts = text.split()
    return text.startswith("/") or (len(parts) >= 2 and parts[0].startswith("@") and parts[1].startswith("/"))


def _trim(text: str, limit: int = 3500) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _telegram_sender_name(message: Message) -> str:
    user = message.from_user
    if not user:
        return "unknown"
    return user.full_name or user.username or str(user.id)


def _max_sender_name(event: Any) -> str:
    sender = dig(event, "message", "sender")
    full_name = getattr(sender, "full_name", None)
    if full_name:
        return str(full_name)
    first_name = dig(sender, "first_name")
    last_name = dig(sender, "last_name")
    name = " ".join(str(x) for x in (first_name, last_name) if x)
    if name:
        return name
    return str(dig(sender, "username") or dig(sender, "user_id") or "unknown")


def _max_sender_is_bot(event: Any) -> bool:
    sender = dig(event, "message", "sender")
    return bool(dig(sender, "is_bot"))


async def forward_telegram_to_max(message: Message) -> bool:
    """Forward a plain Telegram text message to the configured MAX chat."""
    if not BRIDGE_ENABLED or message.chat.id != TELEGRAM_BRIDGE_CHAT_ID:
        return False
    if not message.text:
        return False
    if message.from_user and message.from_user.is_bot:
        return False

    text = message.text.strip()
    if not text or _is_command_text(text) or _is_bridge_text(text):
        return False
    if not MAX_BOT_TOKEN:
        log.warning("Bridge skipped: MAX_BOT_TOKEN is empty")
        return False

    payload = _trim(f"TG | {_telegram_sender_name(message)}:\n{text}")
    max_bot = MaxBot(MAX_BOT_TOKEN)
    try:
        await max_bot.send_message(chat_id=MAX_BRIDGE_CHAT_ID, text=payload)
        log.info("Bridge TG->MAX forwarded chat_id=%s to max_chat_id=%s", message.chat.id, MAX_BRIDGE_CHAT_ID)
    except Exception:
        log.exception("Bridge TG->MAX failed")
        return False
    finally:
        await max_bot.close_session()
    return True


async def forward_max_to_telegram(event: Any) -> bool:
    """Forward a plain MAX text message to the configured Telegram chat."""
    if not BRIDGE_ENABLED or chat_id_from_event(event) != MAX_BRIDGE_CHAT_ID:
        return False
    if _max_sender_is_bot(event):
        return False

    text = text_from_event(event).strip()
    if not text or _is_command_text(text) or _is_bridge_text(text):
        return False

    payload = _trim(f"MAX | {_max_sender_name(event)}:\n{text}")
    telegram_bot = TelegramBot(API_TOKEN)
    try:
        await telegram_bot.send_message(chat_id=TELEGRAM_BRIDGE_CHAT_ID, text=payload, request_timeout=20)
        log.info("Bridge MAX->TG forwarded chat_id=%s to telegram_chat_id=%s", chat_id_from_event(event), TELEGRAM_BRIDGE_CHAT_ID)
    except Exception:
        log.exception("Bridge MAX->TG failed")
        return False
    finally:
        await telegram_bot.session.close()
    return True
