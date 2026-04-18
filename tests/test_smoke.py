"""Дымовые тесты без Telegram и без сети."""
import unittest

from starlette.testclient import TestClient

from bot import __version__
from bot.api.main import app
from bot.state import active, day_key
from bot.status_text import format_day_status_html


class TestAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health(self) -> None:
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "healthy")

    def test_ready(self) -> None:
        r = self.client.get("/ready")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ready"])

    def test_version(self) -> None:
        r = self.client.get("/version")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["service"], "bakery-bot")
        self.assertEqual(data["version"], __version__)

    def test_root(self) -> None:
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["service"], "bakery-bot")
        self.assertEqual(data["version"], __version__)
        self.assertEqual(data["status"], "ok")

    def test_status_shape(self) -> None:
        r = self.client.get("/status")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("date", data)
        self.assertEqual(data["date"], day_key())
        self.assertIn("summary", data)
        self.assertIn("all_done", data["summary"])
        tasks = data["tasks"]
        for name in ("milk", "bakery", "freezer", "opening", "cash", "closing"):
            self.assertIn(name, tasks)


class TestStatusText(unittest.TestCase):
    def test_format_day_status_html(self) -> None:
        text = format_day_status_html(day_key())
        self.assertIn("Статус за", text)
        self.assertIn("Молочка", text)
        self.assertIn("Заморозка", text)


class TestImports(unittest.TestCase):
    def test_handlers_import(self) -> None:
        from bot.handlers import commands_router, content_router, callbacks_router

        self.assertIsNotNone(commands_router)
        self.assertIsNotNone(content_router)
        self.assertIsNotNone(callbacks_router)


def tearDownModule() -> None:
    """Не оставлять тестовые ключи в глобальном state между прогонами."""
    active.clear()
    import bot.state as state_mod

    state_mod.awaiting = None


if __name__ == "__main__":
    unittest.main()
