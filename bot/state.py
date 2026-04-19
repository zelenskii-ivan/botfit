"""Управление состоянием задач."""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

log = logging.getLogger(__name__)

SHELF_HISTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "shelf_history.json"

shelf: Dict[str, Any] = {
    "today_remainders": None,
    "sales_history": {},
    "weather": None,
    "last_recommendation": None,
    "recommendation_accepted": False,
}


def day_key() -> str:
    """Ключ текущего дня для хранения состояния."""
    return datetime.now().strftime("%Y-%m-%d")


# active[(date, task)] = {"status": "...", "photo": bool, "video": bool, ...}
active: Dict[Tuple[str, str], Dict] = {}

# awaiting = что бот ждёт СЕЙЧАС по задаче
# awaiting = {"task": str, "need": "photo"|"video"|"photo_only", "until": datetime}
awaiting: Optional[Dict] = None


def get_task(task: str) -> Dict:
    """Получить или создать запись задачи на сегодня."""
    k = (day_key(), task)
    if k not in active:
        active[k] = {
            "status": "waiting",
            "photo": False,
            "video": False,
            "created_at": datetime.now(),
        }
    return active[k]


def is_done(task: str) -> bool:
    """Проверить, выполнена ли задача."""
    k = (day_key(), task)
    st = active.get(k)
    if not st:
        return False
    if task == "bakery":
        return st.get("photo") is True
    if task == "freezer":
        return st.get("photo") is True
    if task == "milk":
        return st.get("photo") is True and st.get("video") is True
    if task == "opening":
        return st.get("checklist_done") is True
    if task == "closing":
        return st.get("checklist_done") is True
    if task == "cash":
        return st.get("checklist_done") is True
    if task == "shelf":
        return st.get("analysis_done") is True
    return False


def load_shelf_persist() -> None:
    global shelf
    if not SHELF_HISTORY_PATH.is_file():
        return
    try:
        raw = json.loads(SHELF_HISTORY_PATH.read_text(encoding="utf-8"))
        shelf["sales_history"] = raw.get("sales_history", {})
        shelf["last_recommendation"] = raw.get("last_recommendation")
        shelf["recommendation_accepted"] = raw.get("recommendation_accepted", False)
    except Exception as e:
        log.warning("load_shelf_persist: %s", e)


def save_shelf_persist() -> None:
    SHELF_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "sales_history": shelf.get("sales_history", {}),
        "last_recommendation": shelf.get("last_recommendation"),
        "recommendation_accepted": shelf.get("recommendation_accepted", False),
    }
    SHELF_HISTORY_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def set_await(task: str, need: str, minutes: int = 30, chat_id: Optional[int] = None) -> None:
    """Установить ожидание контента от пользователя."""
    global awaiting
    from bot.config import GROUP_ID
    awaiting = {
        "task": task,
        "need": need,
        "until": datetime.now() + timedelta(minutes=minutes),
        "chat_id": chat_id or GROUP_ID,
    }


def clear_await() -> None:
    """Сбросить ожидание."""
    global awaiting
    awaiting = None


def get_awaiting() -> Optional[Dict]:
    """Получить текущее ожидание."""
    return awaiting


def get_day_status(date: str) -> Dict:
    """Получить статус всех задач за день."""
    return {
        "milk": active.get((date, "milk")),
        "bakery": active.get((date, "bakery")),
        "freezer": active.get((date, "freezer")),
        "opening": active.get((date, "opening")),
        "cash": active.get((date, "cash")),
        "closing": active.get((date, "closing")),
    }
