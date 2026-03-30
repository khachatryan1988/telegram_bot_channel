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
        f"Օգտատերերի ընդհանուր քանակը՝ {total_users}\n"
        f"Հաստատված օգտատերեր՝ {verified_users}\n"
        f"Ակտիվ մասնակիցներ՝ {eligible_users}"
    )

    await message.answer(text)


@router.message(Command("participants"))
async def participants_handler(message: Message) -> None:
    if message.from_user is None:
        return

    settings = get_settings()

    eligible_users = get_eligible_users(settings)
    await message.answer(f"Ակտիվ մասնակիցների քանակը՝ {eligible_users}")


@router.message(Command("draw"))
async def draw_handler(message: Message) -> None:
    if message.from_user is None:
        return

    settings = get_settings()

    result = await draw_winner(message.bot, settings)
    if result is None:
        await message.answer("Չհաջողվեց ընտրել հաղթող։ Ակտիվ մասնակիցներ չկան։")
        return

    username = f"@{result.get('username')}" if result.get("username") else "-"
    first_name = result.get("first_name") or "-"
    last_name = result.get("last_name") or "-"

    await message.answer(
        f"Հաղթողը ընտրված է 🎉\n\n"
        f"ID՝ {result['user_id']}\n"
        f"Username՝ {username}\n"
        f"Անուն՝ {first_name}\n"
        f"Ազգանուն՝ {last_name}\n\n"
        f"Վերջնաժամկետ՝ {result['deadline_at']}"
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
                f"Վերախաղարկումը դեռ հասանելի չէ։ Վերջնաժամկետը՝ {deadline_at}"
            )
            return

    result = await redraw_winner(message.bot, settings)
    if result is None:
        await message.answer("Չհաջողվեց ընտրել նոր հաղթող։")
        return

    username = f"@{result.get('username')}" if result.get("username") else "-"
    first_name = result.get("first_name") or "-"
    last_name = result.get("last_name") or "-"

    await message.answer(
        f"Նոր հաղթողը ընտրված է 🎉\n\n"
        f"ID՝ {result['user_id']}\n"
        f"Username՝ {username}\n"
        f"Անուն՝ {first_name}\n"
        f"Ազգանուն՝ {last_name}\n\n"
        f"Վերջնաժամկետ՝ {result['deadline_at']}"
    )


@router.message(Command("winner"))
async def winner_handler(message: Message) -> None:
    if message.from_user is None:
        return

    settings = get_settings()

    info = get_active_winner_info(settings)
    if info is None:
        await message.answer("Այս պահին ակտիվ հաղթող չկա։")
        return

    display_name = info.get("username") or info.get("first_name") or str(info["tg_id"])

    await message.answer(
        f"Ընթացիկ հաղթող՝ {display_name}\n"
        f"Կարգավիճակ՝ {info.get('status') or '-'}\n"
        f"Ծանուցված՝ {info.get('winner_notified_at') or '-'}\n"
        f"Վերջնաժամկետ՝ {info.get('response_deadline_at') or info.get('deadline_at') or '-'}\n"
        f"Պատասխանել է՝ {info.get('responded_at') or '-'}"
    )