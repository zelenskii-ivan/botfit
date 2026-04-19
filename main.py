"""Точка входа: запуск бота и API."""
import asyncio
import logging
import os

from dotenv import load_dotenv
load_dotenv()

LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)  # INFO, DEBUG, WARNING
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot import __version__
from bot.config import API_TOKEN, API_HOST, API_PORT
from bot.app import init_app
from bot.handlers import commands_router, content_router, callbacks_router
from bot.scheduler import setup_schedule
from bot.state import load_shelf_persist

RUN_API = os.getenv("RUN_API", "true").lower() == "true"


async def run_bot():
    """Запуск Telegram-бота."""
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    scheduler = AsyncIOScheduler()

    init_app(bot, scheduler)

    load_shelf_persist()

    dp.include_router(commands_router)
    dp.include_router(callbacks_router)
    dp.include_router(content_router)

    await setup_schedule(scheduler)

    me = await bot.get_me()
    log.info("Bakery Bot v%s started: @%s, GROUP_ID=%s", __version__, me.username, os.getenv("GROUP_ID"))

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


def run_api():
    """Запуск FastAPI (health check, мониторинг)."""
    import uvicorn
    from bot.api.main import app
    uvicorn.run(app, host=API_HOST, port=API_PORT)


if __name__ == "__main__":
    if not RUN_API:
        asyncio.run(run_bot())
    else:
        import threading
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        asyncio.run(run_bot())
