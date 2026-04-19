"""Анализ фото полки — OpenAI Vision (gpt-4o)."""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from bot.config import OPENAI_API_KEY, OPENAI_BASE_URL

log = logging.getLogger(__name__)

VISION_MODEL = "gpt-4o"

VISION_PROMPT = """На фото — полка с выпечкой в кофейне. Перечисли все видимые позиции и для каждой дай оценку остатка: много / немного / почти нет / пусто. Ответь строго в JSON:
[{"name": "...", "remainder": "много|немного|почти нет|пусто"}, ...]"""


def _parse_json_array(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    m = re.search(r"\[[\s\S]*\]", text)
    if not m:
        raise ValueError("JSON-массив не найден в ответе модели")
    return json.loads(m.group(0))


async def analyze_shelf_image_bytes(image_bytes: bytes, mime: str = "image/jpeg") -> list[dict[str, Any]]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY не задан (нужен для Vision)")

    import base64

    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    url = f"data:{mime};base64,{b64}"

    from openai import AsyncOpenAI

    kw: dict = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE_URL:
        kw["base_url"] = OPENAI_BASE_URL
    client = AsyncOpenAI(**kw)

    resp = await client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": VISION_PROMPT},
                    {"type": "image_url", "image_url": {"url": url}},
                ],
            }
        ],
        max_tokens=1500,
        temperature=0.2,
    )
    raw = (resp.choices[0].message.content or "").strip()
    log.debug("vision raw: %s", raw[:500])
    items = _parse_json_array(raw)
    out: list[dict[str, Any]] = []
    for it in items:
        name = str(it.get("name", "")).strip()
        rem = str(it.get("remainder", "")).strip().lower()
        if not name:
            continue
        for key in ("много", "немного", "почти нет", "пусто"):
            if key in rem:
                rem = key
                break
        out.append({"name": name, "remainder": rem})
    return out
