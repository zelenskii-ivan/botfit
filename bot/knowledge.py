"""Загрузка базы знаний для ИИ и команды /topics."""
import os
from pathlib import Path

_DEFAULT_FAQ = Path(__file__).resolve().parent / "faq_knowledge.md"


def faq_file_path() -> Path:
    """Путь к файлу FAQ (переопределяется FAQ_PATH в .env)."""
    override = os.getenv("FAQ_PATH", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return _DEFAULT_FAQ


def load_faq_text() -> str:
    """Текст базы знаний для промпта."""
    path = faq_file_path()
    if not path.is_file():
        return (
            "(Файл базы знаний не найден: укажите FAQ_PATH или положите faq_knowledge.md рядом с пакетом bot.)"
        )
    return path.read_text(encoding="utf-8")


def list_topic_titles() -> list[str]:
    """Заголовки разделов (строки, начинающиеся с #)."""
    text = load_faq_text()
    titles: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            t = line.lstrip("#").strip()
            if t:
                titles.append(t)
    return titles
