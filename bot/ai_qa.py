"""Ответы на вопросы через LLM по базе знаний."""
import logging
import time

from bot.config import AI_ENABLED, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from bot.knowledge import load_faq_text

log = logging.getLogger(__name__)

# user_id -> timestamps запросов за последнюю минуту
_rate_bucket: dict[int, list[float]] = {}
_MAX_PER_MINUTE = 8


def _rate_ok(user_id: int) -> bool:
    now = time.time()
    window = [t for t in _rate_bucket.get(user_id, []) if now - t < 60.0]
    if len(window) >= _MAX_PER_MINUTE:
        return False
    window.append(now)
    _rate_bucket[user_id] = window
    return True


async def answer_faq_question(user_id: int, question: str) -> str:
    """
    Краткий ответ на русском по базе знаний.
    Без сети / без ключа — возвращает текст-заглушку.
    """
    q = (question or "").strip()
    if len(q) < 2:
        return "Напишите вопрос текстом, например: /ask Когда подтверждать кассу?"

    if not _rate_ok(user_id):
        return "Слишком много запросов. Подождите минуту и попробуйте снова."

    if not AI_ENABLED or not OPENAI_API_KEY:
        return (
            "ИИ-ответы отключены. Добавьте в .env: <code>OPENAI_API_KEY=...</code> "
            "и <code>AI_ENABLED=true</code>, затем перезапустите бота."
        )

    faq = load_faq_text()
    system = (
        "Ты помощник сотрудников кофейни/пекарни. Отвечай кратко по-русски, дружелюбно. "
        "Используй ТОЛЬКО информацию из базы знаний ниже. "
        "Если в базе нет ответа, напиши одно предложение: что уточнить у старшего смены или управляющего. "
        "Не выдумывай цифры времени и расписания, если их нет в базе — скажи «см. расписание в боте /status».\n\n"
        f"<база_знаний>\n{faq}\n</база_знаний>"
    )

    try:
        from openai import AsyncOpenAI

        client_kw: dict = {"api_key": OPENAI_API_KEY}
        if OPENAI_BASE_URL:
            client_kw["base_url"] = OPENAI_BASE_URL
        client = AsyncOpenAI(**client_kw)
        resp = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": q},
            ],
            max_tokens=500,
            temperature=0.3,
        )
        choice = resp.choices[0].message.content
        return (choice or "").strip() or "Пустой ответ модели. Попробуйте переформулировать вопрос."
    except Exception as e:
        log.exception("answer_faq_question failed: %s", e)
        return "Не удалось получить ответ ИИ. Попробуйте позже или обратитесь к управляющему."


def is_ai_configured() -> bool:
    """Есть ли ключ и включён ли ИИ (для подсказок в /topics)."""
    return bool(AI_ENABLED and OPENAI_API_KEY)
