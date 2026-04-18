"""Настройка планировщика задач."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.tasks import (
    request_milk,
    request_bakery,
    request_freezer,
    request_opening,
    request_cash,
    request_closing,
    request_sanitary,
    request_equipment,
    send_memo,
    get_schedule_config,
)


async def _job_milk():
    from bot.app import bot, scheduler
    await request_milk(bot, scheduler)


async def _job_bakery():
    from bot.app import bot, scheduler
    await request_bakery(bot, scheduler)


async def _job_freezer():
    from bot.app import bot, scheduler
    await request_freezer(bot, scheduler)


async def _job_opening():
    from bot.app import bot, scheduler
    await request_opening(bot, scheduler)


async def _job_cash():
    from bot.app import bot, scheduler
    await request_cash(bot, scheduler)


async def _job_closing():
    from bot.app import bot, scheduler
    await request_closing(bot, scheduler)


async def _job_sanitary():
    from bot.app import bot, scheduler
    await request_sanitary(bot, scheduler)


async def _job_equipment():
    from bot.app import bot, scheduler
    await request_equipment(bot, scheduler)


async def _job_memo():
    from bot.app import bot
    await send_memo(bot)


async def setup_schedule(scheduler: AsyncIOScheduler) -> None:
    """Добавить cron-задачи в планировщик."""
    cfg = get_schedule_config()

    scheduler.add_job(_job_milk, "cron", day_of_week=cfg["milk"]["day_of_week"],
                      hour=cfg["milk"]["hour"], minute=cfg["milk"]["minute"])
    scheduler.add_job(_job_bakery, "cron", hour=cfg["bakery"]["hour"], minute=cfg["bakery"]["minute"])
    scheduler.add_job(_job_freezer, "cron", hour=cfg["freezer"]["hour"], minute=cfg["freezer"]["minute"])
    scheduler.add_job(_job_opening, "cron", hour=cfg["opening"]["hour"], minute=cfg["opening"]["minute"])
    scheduler.add_job(_job_cash, "cron", hour=cfg["cash"]["hour"], minute=cfg["cash"]["minute"])
    scheduler.add_job(_job_closing, "cron", hour=cfg["closing"]["hour"], minute=cfg["closing"]["minute"])
    scheduler.add_job(_job_memo, "cron", hour=cfg["memo_1"]["hour"], minute=cfg["memo_1"]["minute"])
    scheduler.add_job(_job_memo, "cron", hour=cfg["memo_2"]["hour"], minute=cfg["memo_2"]["minute"])

    if cfg["sanitary"]["enabled"]:
        scheduler.add_job(
            _job_sanitary,
            "cron",
            hour=cfg["sanitary"]["hour"],
            minute=cfg["sanitary"]["minute"],
        )
    if cfg["equipment"]["enabled"]:
        scheduler.add_job(
            _job_equipment,
            "cron",
            hour=cfg["equipment"]["hour"],
            minute=cfg["equipment"]["minute"],
        )

    scheduler.start()
