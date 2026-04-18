"""Глобальные объекты приложения (bot, scheduler) для использования в handlers."""
from typing import Optional

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot: Optional[Bot] = None
scheduler: Optional[AsyncIOScheduler] = None


def init_app(bot_instance: Bot, scheduler_instance: AsyncIOScheduler) -> None:
    """Инициализировать глобальные объекты при старте."""
    global bot, scheduler
    bot = bot_instance
    scheduler = scheduler_instance
