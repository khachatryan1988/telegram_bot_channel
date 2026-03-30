from aiogram import Bot

from config import Settings


def create_bot(settings: Settings) -> Bot:
    return Bot(token=settings.bot_token)




