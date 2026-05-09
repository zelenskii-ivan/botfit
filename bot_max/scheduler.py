"""Scheduler setup for MAX bot."""
from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import MAX_GROUP_ID
from bot.memo import MEMO_TEXT
from bot.tasks import (
    get_schedule_config,
    request_bakery,
    request_cash,
    request_closing,
    request_freezer,
    request_milk,
    request_opening,
    request_shelf_photo,
)
from bot_max.adapter import MaxBotAdapter


async def setup_max_schedule(scheduler: AsyncIOScheduler, bot: MaxBotAdapter) -> None:
    cfg = get_schedule_config()

    async def job_milk() -> None:
        await request_milk(bot, scheduler, MAX_GROUP_ID)

    async def job_bakery() -> None:
        await request_bakery(bot, scheduler, MAX_GROUP_ID)

    async def job_freezer() -> None:
        await request_freezer(bot, scheduler, MAX_GROUP_ID)

    async def job_opening() -> None:
        await request_opening(bot, scheduler, MAX_GROUP_ID)

    async def job_cash() -> None:
        await request_cash(bot, scheduler, MAX_GROUP_ID)

    async def job_closing() -> None:
        await request_closing(bot, scheduler, MAX_GROUP_ID)

    async def job_memo() -> None:
        await bot.send_message(MAX_GROUP_ID, "⏰ <b>Напоминание: обязательные работы</b>\n\n" + MEMO_TEXT)

    async def job_shelf() -> None:
        await request_shelf_photo(bot, scheduler, MAX_GROUP_ID)

    scheduler.add_job(job_milk, "cron", day_of_week=cfg["milk"]["day_of_week"], hour=cfg["milk"]["hour"], minute=cfg["milk"]["minute"])
    scheduler.add_job(job_bakery, "cron", hour=cfg["bakery"]["hour"], minute=cfg["bakery"]["minute"])
    scheduler.add_job(job_freezer, "cron", hour=cfg["freezer"]["hour"], minute=cfg["freezer"]["minute"])
    scheduler.add_job(job_opening, "cron", hour=cfg["opening"]["hour"], minute=cfg["opening"]["minute"])
    scheduler.add_job(job_cash, "cron", hour=cfg["cash"]["hour"], minute=cfg["cash"]["minute"])
    scheduler.add_job(job_closing, "cron", hour=cfg["closing"]["hour"], minute=cfg["closing"]["minute"])
    scheduler.add_job(job_memo, "cron", hour=cfg["memo_1"]["hour"], minute=cfg["memo_1"]["minute"])
    scheduler.add_job(job_memo, "cron", hour=cfg["memo_2"]["hour"], minute=cfg["memo_2"]["minute"])

    if cfg["shelf"]["enabled"]:
        scheduler.add_job(job_shelf, "cron", hour=cfg["shelf"]["hour"], minute=cfg["shelf"]["minute"])

    scheduler.start()

