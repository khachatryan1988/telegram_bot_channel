import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Update

from config import Settings
from app.repositories.processed_updates import remember_update_id

logger = logging.getLogger(__name__)


class DedupUpdateMiddleware(BaseMiddleware):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        update_id = event.update_id
        if not remember_update_id(self._settings, update_id):
            logger.info("Skipping duplicate update", extra={"update_id": update_id})
            return None

        return await handler(event, data)




