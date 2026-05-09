"""Точка входа для MAX messenger."""
from __future__ import annotations

import asyncio
import logging
import os
import threading

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from maxapi import Bot, Dispatcher

from bot import __version__
from bot.config import API_HOST, API_PORT, MAX_BOT_TOKEN, MAX_GROUP_ID
from bot.state import load_shelf_persist
from bot_max.adapter import MaxBotAdapter
from bot_max.handlers import register_handlers
from bot_max.scheduler import setup_max_schedule

RUN_API = os.getenv("RUN_API", "true").lower() == "true"


async def run_max_bot() -> None:
    if not MAX_BOT_TOKEN:
        raise RuntimeError("MAX_BOT_TOKEN не задан в .env")

    raw_bot = Bot(MAX_BOT_TOKEN)
    bot = MaxBotAdapter(raw_bot)
    dp = Dispatcher()
    scheduler = AsyncIOScheduler()

    load_shelf_persist()
    register_handlers(dp, bot, scheduler)
    await setup_max_schedule(scheduler, bot)

    log.info("Bakery Bot MAX v%s started, MAX_GROUP_ID=%s", __version__, MAX_GROUP_ID)
    await dp.start_polling(raw_bot)


def run_api() -> None:
    import uvicorn
    from bot.api.main import app

    uvicorn.run(app, host=API_HOST, port=API_PORT)


if __name__ == "__main__":
    if RUN_API:
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
    asyncio.run(run_max_bot())

