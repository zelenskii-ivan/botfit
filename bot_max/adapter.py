"""Small compatibility wrapper around MAX Bot API client."""
from __future__ import annotations

import re
from typing import Any


_TAG_RE = re.compile(r"</?(?:b|strong|i|em|u|s|code|pre)>")
_BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


def html_to_max_text(text: str) -> str:
    """Convert the Telegram-oriented HTML messages to plain MAX-safe text."""
    text = _BR_RE.sub("\n", text)
    text = _TAG_RE.sub("", text)
    return (
        text.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
    )


class MaxBotAdapter:
    """Duck-typed subset of aiogram.Bot used by bot.tasks."""

    def __init__(self, bot: Any):
        self._bot = bot

    async def send_message(self, chat_id: int, text: str, **kwargs: Any) -> Any:
        return await self._bot.send_message(
            chat_id=chat_id,
            text=html_to_max_text(text),
            attachments=kwargs.get("attachments"),
        )

