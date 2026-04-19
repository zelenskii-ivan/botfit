"""Единое HTML-форматирование статуса задач за день."""
from bot.state import get_day_status


def format_day_status_html(d: str) -> str:
    """Текст статуса за дату `d` (YYYY-MM-DD) для сообщений бота."""
    status = get_day_status(d)
    milk = status["milk"]
    bakery = status["bakery"]
    freezer = status["freezer"]
    opening = status["opening"]
    cash = status["cash"]
    closing = status["closing"]

    def fmt_milk() -> str:
        if not milk:
            return "—"
        return (
            f"фото={'✅' if milk.get('photo') else '❌'}, "
            f"видео={'✅' if milk.get('video') else '❌'}"
        )

    def fmt_photo_only(data) -> str:
        if not data:
            return "—"
        return f"фото={'✅' if data.get('photo') else '❌'}"

    def fmt_ck(data) -> str:
        if not data:
            return "—"
        return "✅" if data.get("checklist_done") else "❌"

    return (
        f"📌 <b>Статус за {d}</b>\n"
        f"🧊 Молочка: {fmt_milk()}\n"
        f"🥐 Выпечка: {fmt_photo_only(bakery)}\n"
        f"❄️ Заморозка: {fmt_photo_only(freezer)}\n"
        f"🌅 Открытие: {fmt_ck(opening)}\n"
        f"💰 Касса: {fmt_ck(cash)}\n"
        f"🌙 Закрытие: {fmt_ck(closing)}"
    )
