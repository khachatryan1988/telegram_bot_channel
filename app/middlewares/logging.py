import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

logger = logging.getLogger(__name__)


class UpdateLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        update = data.get("event_update")
        logger.info(
            "Handling update",
            extra=self._build_context(event, update),
        )
        result = await handler(event, data)
        logger.info(
            "Handled update",
            extra=self._build_context(event, update),
        )
        return result

    def _build_context(
        self,
        event: TelegramObject,
        update: Update | None,
    ) -> dict[str, Any]:
        context: dict[str, Any] = {
            "event_type": type(event).__name__,
            "update_id": update.update_id if update else None,
        }

        if isinstance(event, Message) and event.from_user is not None:
            context["tg_user_id"] = event.from_user.id
            context["chat_id"] = event.chat.id
            context["message_text"] = event.text
        elif isinstance(event, CallbackQuery) and event.from_user is not None:
            context["tg_user_id"] = event.from_user.id
            context["callback_data"] = event.data

        return context




