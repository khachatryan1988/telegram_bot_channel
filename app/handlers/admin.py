from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import get_settings
from app.repositories.stats import get_eligible_users, get_total_users, get_verified_users
from app.repositories.winners import get_active_winner_info, get_pending_winner_info
from app.services.draw import draw_winner, redraw_winner
from app.utils.time import is_past_due
from app.utils.admin import AdminFilter

router = Router()
router.message.filter(AdminFilter())


@router.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    if message.from_user is None:
        return

    settings = get_settings()

    total_users = get_total_users(settings)
    verified_users = get_verified_users(settings)
    eligible_users = get_eligible_users(settings)

    text = (
        "Всего пользователей: {total}\n"
        "Подтверждённых участников: {verified}\n"
        "Активных участников: {eligible}"
    ).format(total=total_users, verified=verified_users, eligible=eligible_users)

    await message.answer(text)


@router.message(Command("participants"))
async def participants_handler(message: Message) -> None:
    if message.from_user is None:
        return

    settings = get_settings()

    eligible_users = get_eligible_users(settings)
    await message.answer(f"Активных участников: {eligible_users}")


@router.message(Command("draw"))
async def draw_handler(message: Message) -> None:
    if message.from_user is None:
        return

    settings = get_settings()

    result = await draw_winner(message.bot, settings)
    if result is None:
        await message.answer("Не удалось выбрать победителя. Нет подходящих активных участников.")
        return

    await message.answer(
        f"Победитель выбран. User ID: {result['user_id']}\n"
        f"Дедлайн: {result['deadline_at']}"
    )


@router.message(Command("redraw"))
async def redraw_handler(message: Message) -> None:
    if message.from_user is None:
        return

    settings = get_settings()

    pending_winner = get_pending_winner_info(settings)
    if pending_winner is not None:
        deadline_at = pending_winner.get("response_deadline_at") or pending_winner.get(
            "deadline_at"
        )
        if deadline_at is not None and not is_past_due(deadline_at):
            await message.answer(
                f"Повторный розыгрыш пока недоступен. Дедлайн текущего победителя: {deadline_at}"
            )
            return

    result = await redraw_winner(message.bot, settings)
    if result is None:
        await message.answer("Не удалось выбрать нового победителя.")
        return

    await message.answer(
        f"Новый победитель выбран. User ID: {result['user_id']}\n"
        f"Дедлайн: {result['deadline_at']}"
    )


@router.message(Command("winner"))
async def winner_handler(message: Message) -> None:
    if message.from_user is None:
        return

    settings = get_settings()

    info = get_active_winner_info(settings)
    if info is None:
        await message.answer("Активного победителя нет.")
        return

    display_name = info.get("username") or info.get("first_name") or str(info["tg_id"])
    await message.answer(
        f"Текущий победитель: {display_name}\n"
        f"Статус: {info.get('status') or '-'}\n"
        f"Уведомлён: {info.get('winner_notified_at') or '-'}\n"
        f"Дедлайн ответа: {info.get('response_deadline_at') or info.get('deadline_at') or '-'}\n"
        f"Ответил: {info.get('responded_at') or '-'}"
    )
