"""Сезон модуля полки: 27 апреля — 20 мая 2026."""
from datetime import date

from bot.config import SHELF_SEASON_BYPASS

SHELF_SEASON_START = date(2026, 4, 27)
SHELF_SEASON_END = date(2026, 5, 20)


def is_shelf_season_active() -> bool:
    if SHELF_SEASON_BYPASS:
        return True
    today = date.today()
    return SHELF_SEASON_START <= today <= SHELF_SEASON_END
