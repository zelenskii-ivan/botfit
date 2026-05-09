"""Helpers for reading MAX SDK events without depending on every payload shape."""
from __future__ import annotations

from typing import Any


def dig(obj: Any, *path: str) -> Any:
    cur = obj
    for part in path:
        if cur is None:
            return None
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            cur = getattr(cur, part, None)
    return cur


def chat_id_from_event(event: Any) -> int | None:
    value = (
        getattr(event, "chat_id", None)
        or dig(event, "message", "recipient", "chat_id")
        or dig(event, "message", "chat_id")
        or dig(event, "chat", "id")
    )
    return int(value) if value is not None else None


def text_from_event(event: Any) -> str:
    return (
        dig(event, "message", "body", "text")
        or dig(event, "message", "text")
        or getattr(event, "text", "")
        or ""
    )


def attachments_from_event(event: Any) -> list[Any]:
    attachments = dig(event, "message", "body", "attachments") or dig(event, "message", "attachments") or []
    return list(attachments)


def attachment_type(attachment: Any) -> str:
    return str(dig(attachment, "type") or getattr(attachment, "type", "") or "").lower()


def has_image(event: Any) -> bool:
    return any(attachment_type(a) in {"image", "photo"} for a in attachments_from_event(event))


def has_video(event: Any) -> bool:
    return any(attachment_type(a) in {"video", "video_note"} for a in attachments_from_event(event))

