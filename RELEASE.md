# Релиз Bakery Bot

Текущая версия задаётся в `bot/__init__.py` (`__version__`).

## Перед публикацией

1. Обновите `CHANGELOG.md` и номер в `bot/__init__.py`.
2. Проверка локально:

   ```bash
   python -m compileall -q .
   python main.py   # или только импорт: python -c "from bot import __version__; print(__version__)"
   curl -s http://127.0.0.1:8080/version   # при RUN_API=true
   ```

3. Docker:

   ```bash
   docker compose build --no-cache
   docker compose up -d
   curl -s http://127.0.0.1:8080/version
   ```

## Git: тег версии

Если корень репозитория — каталог с этим проектом (не родительская папка):

```bash
git add -A
git status
git commit -m "Release v1.1.0"
git tag -a v1.1.0 -m "Bakery Bot 1.1.0"
git push origin main
git push origin v1.1.0
```

При необходимости замените `main` на вашу ветку.

**Remote по умолчанию:** `git@github.com:zelenskii-ivan/botfit.git`

## Клонирование и переключение на тег

Выполняйте команды **по отдельности** (или копируйте без комментария в конце строки — иначе shell может передать `# …` в `git`).

```bash
git clone git@github.com:zelenskii-ivan/botfit.git
cd botfit
git checkout v1.1.0
```

Переключение на тег не обязательно, если вы остались на `main` и он указывает на тот же коммит.

## Артефакт релиза

- Исходный код в ветке и тег `v1.1.0`.
- Образ Docker (если используете registry): `docker tag bakery-bot:latest your-registry/bakery-bot:1.1.0`.
