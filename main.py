import asyncio
from aiogram import Bot, Dispatcher

from config import get_settings
from app.db import init_db
from app.handlers.admin import router as admin_router
from app.handlers.user import router as user_router
from app.logging_setup import configure_logging
from app.middlewares import (
    DedupUpdateMiddleware,
    ErrorMiddleware,
    UpdateLoggingMiddleware,
)


async def main() -> None:
    configure_logging()

    settings = get_settings()
    init_db(settings)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.update.outer_middleware(DedupUpdateMiddleware(settings))
    dp.message.outer_middleware(ErrorMiddleware())
    dp.callback_query.outer_middleware(ErrorMiddleware())
    dp.message.middleware(UpdateLoggingMiddleware())
    dp.callback_query.middleware(UpdateLoggingMiddleware())

    dp.include_router(user_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())




