from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import get_settings
from app.repositories.referrals import (
    get_all_referrals,
    get_inviter_by_invited_tg_id,
    get_referrals_by_referrer_tg_id,
)
from app.repositories.stats import get_eligible_users, get_total_users, get_verified_users
from app.repositories.winners import get_active_winner_info, get_pending_winner_info
from app.services.draw import draw_winner, redraw_winner
from app.utils.admin import AdminFilter
from app.utils.time import is_past_due

router = Router()
router.message.filter(AdminFilter())


def _format_username(username: str | None) -> str:
    return f"@{username}" if username else "-"


def _format_name(first_name: str | None, last_name: str | None) -> str:
    full_name = " ".join(part for part in [first_name, last_name] if part)
    return full_name if full_name else "-"


@router.message(Command("admin"))
async def admin_menu_handler(message: Message) -> None:
    await message.answer(
        "🔧 Ադմին մենյու\n\n"
        "/stats — վիճակագրություն\n"
        "/participants — ակտիվ մասնակիցների քանակը\n"
        "/draw — ընտրել հաղթող\n"
        "/redraw — վերախաղարկել\n"
        "/winner — ընթացիկ հաղթող\n"
        "/referrals — ով ում է հրավիրել\n"
        "/referrals <tg_id> — կոնկրետ օգտատիրոջ հրավերները\n"
        "/whoinvited <tg_id> — տեսնել, թե ով է հրավիրել օգտատիրոջը"
    )


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

    username = _format_username(result.get("username"))
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

    username = _format_username(result.get("username"))
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


@router.message(Command("referrals"))
async def referrals_handler(message: Message) -> None:
    if message.from_user is None:
        return

    settings = get_settings()
    parts = (message.text or "").split(maxsplit=1)

    if len(parts) > 1 and parts[1].isdigit():
        referrer_tg_id = int(parts[1])
        rows = get_referrals_by_referrer_tg_id(settings, referrer_tg_id)

        if not rows:
            await message.answer("Այս օգտատիրոջ հրավերները չեն գտնվել։")
            return

        lines = [f"Օգտատիրոջ հրավերները՝ {referrer_tg_id}\n"]

        for i, row in enumerate(rows, start=1):
            invited_username = _format_username(row["invited_username"])
            invited_name = _format_name(
                row["invited_first_name"],
                row["invited_last_name"],
            )
            verified_text = "այո" if row["is_verified"] else "ոչ"

            lines.append(
                f"{i}. "
                f"Ներքին ID՝ {row['invited_user_id']} | "
                f"TG ID՝ {row['invited_tg_id'] or '-'} | "
                f"Username՝ {invited_username} | "
                f"Անուն՝ {invited_name} | "
                f"Հաստատված՝ {verified_text}"
            )

        text = "\n".join(lines)
        for i in range(0, len(text), 4000):
            await message.answer(text[i:i + 4000])
        return

    rows = get_all_referrals(settings)

    if not rows:
        await message.answer("Հրավերների տվյալներ չկան։")
        return

    lines = ["Ով ում է հրավիրել՝\n"]

    for i, row in enumerate(rows, start=1):
        referrer_username = _format_username(row["referrer_username"])
        referrer_name = _format_name(
            row["referrer_first_name"],
            row["referrer_last_name"],
        )

        invited_username = _format_username(row["invited_username"])
        invited_name = _format_name(
            row["invited_first_name"],
            row["invited_last_name"],
        )

        verified_text = "այո" if row["is_verified"] else "ոչ"

        lines.append(
            f"{i}. "
            f"Հրավիրող՝ [ID {row['referrer_user_id']}] {referrer_username} | {referrer_name} | TG ID՝ {row['referrer_tg_id'] or '-'} "
            f"→ "
            f"Հրավիրված՝ [ID {row['invited_user_id']}] {invited_username} | {invited_name} | TG ID՝ {row['invited_tg_id'] or '-'} | "
            f"Հաստատված՝ {verified_text}"
        )

    text = "\n".join(lines)
    for i in range(0, len(text), 4000):
        await message.answer(text[i:i + 4000])


@router.message(Command("whoinvited"))
async def who_invited_handler(message: Message) -> None:
    if message.from_user is None:
        return

    settings = get_settings()
    parts = (message.text or "").split(maxsplit=1)

    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Օգտագործում՝ /whoinvited <tg_id>")
        return

    invited_tg_id = int(parts[1])
    row = get_inviter_by_invited_tg_id(settings, invited_tg_id)

    if row is None:
        await message.answer("Տվյալ օգտատիրոջ հրավիրողը չի գտնվել։")
        return

    referrer_username = _format_username(row["referrer_username"])
    referrer_name = _format_name(
        row["referrer_first_name"],
        row["referrer_last_name"],
    )
    invited_username = _format_username(row["invited_username"])
    invited_name = _format_name(
        row["invited_first_name"],
        row["invited_last_name"],
    )
    verified_text = "այո" if row["is_verified"] else "ոչ"

    await message.answer(
        f"Հրավիրված օգտատեր՝ {invited_name}\n"
        f"Username՝ {invited_username}\n"
        f"TG ID՝ {row['invited_tg_id'] or '-'}\n"
        f"Հաստատված՝ {verified_text}\n\n"
        f"Հրավիրող՝ {referrer_name}\n"
        f"Username՝ {referrer_username}\n"
        f"TG ID՝ {row['referrer_tg_id'] or '-'}"
    )