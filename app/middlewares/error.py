import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = logging.getLogger(__name__)

USER_ERROR_TEXT = "ХЏХҐХІХ« ХёЦ‚Х¶ХҐЦЃХЎХѕ ХЅХ­ХЎХ¬Ц‰ ФЅХ¶Х¤ЦЂХёЦ‚Хґ ХҐХ¶Ц„ ХґХ« ЦѓХёЦ„ЦЂ ХёЦ‚Х· ХЇЦЂХЇХ«Х¶ ЦѓХёЦЂХ±ХҐХ¬Ц‰"


class ErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception:
            logger.exception("Unhandled bot error")
            await self._notify_user(event)
            return None

    async def _notify_user(self, event: TelegramObject) -> None:
        if isinstance(event, Message):
            await event.answer(USER_ERROR_TEXT)
            return

        if isinstance(event, CallbackQuery):
            try:
                await event.answer(USER_ERROR_TEXT, show_alert=True)
            except Exception:
                logger.exception("Failed to answer callback after error")




