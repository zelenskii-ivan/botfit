"""FastAPI приложение для health check и мониторинга (Timeweb Cloud)."""
from datetime import datetime, timezone

from fastapi import FastAPI

from bot import __version__
from bot.state import day_key, get_day_status, is_done

app = FastAPI(
    title="Bakery Bot API",
    description="Health check и мониторинг бота кофейни",
    version=__version__,
)


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/")
async def root():
    """Корневой endpoint."""
    return {
        "service": "bakery-bot",
        "status": "ok",
        "version": __version__,
        "timestamp": _utc_iso(),
    }


@app.get("/version")
async def version_endpoint():
    return {"service": "bakery-bot", "version": __version__}


@app.get("/health")
async def health():
    """Health check для Timeweb Cloud / load balancer."""
    return {"status": "healthy", "timestamp": _utc_iso()}


@app.get("/ready")
async def ready():
    """Readiness probe (K8s/Docker)."""
    return {"ready": True}


@app.get("/status")
async def status():
    """Текущий статус задач за день (для мониторинга)."""
    d = day_key()
    data = get_day_status(d)
    tasks = {
        "milk": _fmt_task("milk", data["milk"], ["photo", "video"]),
        "bakery": _fmt_task("bakery", data["bakery"], ["photo"]),
        "freezer": _fmt_task("freezer", data["freezer"], ["photo"]),
        "opening": _fmt_task("opening", data["opening"], ["checklist_done"]),
        "cash": _fmt_task("cash", data["cash"], ["checklist_done"]),
        "closing": _fmt_task("closing", data["closing"], ["checklist_done"]),
    }
    return {
        "date": d,
        "tasks": tasks,
        "summary": {
            "all_done": all(t.get("done") for t in tasks.values()),
        },
    }


def _fmt_task(task_name: str, task_data, fields: list[str]) -> dict:
    """Форматировать задачу для API."""
    if not task_data:
        return {"status": "not_started", "done": False}
    out = {f: task_data.get(f, False) for f in fields}
    out["status"] = task_data.get("status", "unknown")
    out["done"] = is_done(task_name)
    return out
