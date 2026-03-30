from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import get_settings


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False
        settings = get_settings()
        return message.from_user.id in settings.admin_ids




