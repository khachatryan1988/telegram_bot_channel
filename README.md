# Domus Giveaway Bot MVP

Минимальный Telegram giveaway bot для канала `@domus_stores_test_1` на `aiogram` и `SQLite`.

## Что умеет MVP
- регистрация участника через `/start` и deep link `ref_<code>`
- проверка подписки на канал
- персональная referral link и прогресс `0/3 ... 3/3`
- eligibility только после нужного числа подтвержденных приглашений
- ручной `/draw` и `/redraw`
- подтверждение ответа победителя кнопкой в течение 48 часов
- хранение draw/winner state в SQLite

## Стек
- Python 3.12+ for local runs, target compatibility is Python 3.14.x
- aiogram 3.26.x
- SQLite
- polling mode

## Структура
- `main.py` — точка входа
- `config.py` — загрузка env
- `texts.py` — Armenian UI texts
- `app/handlers/` — routers для user/admin flow
- `app/services/` — verification/referral/draw logic
- `app/repositories/` — SQL-access слой
- `app/db/` — schema и init logic
- `app/middlewares/` — dedup, logging, error handling
- `tests/` — unit и smoke tests

## Быстрый старт
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env .env
```

Заполните `.env`:
```dotenv
BOT_TOKEN=your_token_here
CHANNEL_USERNAME=@domus_stores_test_1
ADMIN_IDS=123456789
REFERRAL_TARGET=3
WINNER_RESPONSE_HOURS=48
DB_PATH=./db.sqlite3
```

## Запуск
```bash
python3 main.py
```

При старте бот:
- настраивает централизованное логирование
- инициализирует SQLite schema
- подключает routers и middleware

## Production-minimum, который уже есть
- централизованное логирование через `app/logging_setup.py`
- `ErrorMiddleware` для перехвата необработанных исключений
- `DedupUpdateMiddleware` для защиты от повторной обработки `update_id`
- модульная организация через `routers`, без FSM

## Тесты
```bash
pytest
```

Покрыто:
- unit tests для referral logic
- smoke tests для DB init и базовых repositories

## Заметки по эксплуатации
- `ADMIN_IDS` берутся только из env
- победитель выбирается только из eligible users
- перед выдачей победителя повторно проверяется подписка
- если победитель не подтвердил ответ до `response_deadline_at`, админ может сделать `/redraw`
