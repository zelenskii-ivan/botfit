"""Обработчики сообщений бота."""
from .commands import router as commands_router
from .content import router as content_router
from .callbacks import router as callbacks_router

__all__ = ["commands_router", "content_router", "callbacks_router"]
