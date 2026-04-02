from aiogram import F, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import CallbackQuery, Message

from config import get_settings
from texts import (
    CHECK_FAIL,
    CHECK_ERROR,
    CHECK_OK,
    MAIN_MENU,
    PARTICIPATE_INFO,
    PROGRESS_TITLE,
    REF_LINK_TITLE,
    WELCOME,
    WINNER_RESPONSE_CONFIRMED,
    WINNER_RESPONSE_EXPIRED,
    WINNER_RESPONSE_INVALID,
)
from app.keyboards.main import (
    main_menu_keyboard,
    participate_keyboard,
    referral_share_keyboard,
)
from app.repositories.users import create_user, get_user_id_by_tg_id, set_start_param
from app.repositories.referrals import get_referrer_id, set_referrer
from app.repositories.status import ensure_status_row, set_verified
from app.repositories.winners import get_pending_winner_info
from app.services.draw import confirm_winner_response
from app.services.referral import recalc_referral_progress
from app.services.verification import is_user_subscribed
from app.utils.time import is_past_due, utcnow_iso

router = Router()


def _extract_referrer_tg_id(start_param: str) -> int | None:
    if not start_param.startswith("ref_"):
        return None
    ref_code = start_param[4:].strip()
    if not ref_code.isdigit():
        return None
    return int(ref_code)


def _build_ref_link(bot_username: str, tg_user_id: int) -> str:
    username = bot_username.lstrip("@")
    return f"https://t.me/{username}?start=ref_{tg_user_id}"


@router.message(CommandStart())
async def start_handler(message: Message, command: CommandObject) -> None:
    if message.from_user is None:
        return

    settings = get_settings()
    tg_user = message.from_user
    existing_user_id = get_user_id_by_tg_id(settings, tg_user.id)
    is_new_user = existing_user_id is None

    if is_new_user:
        user_id = create_user(
            settings,
            tg_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
        )
        ensure_status_row(settings, user_id)
    else:
        user_id = int(existing_user_id)

    start_param = command.args or ""
    if is_new_user and start_param:
        set_start_param(settings, user_id, start_param)

    if is_new_user and start_param:
        referrer_tg_id = _extract_referrer_tg_id(start_param)
        if referrer_tg_id and referrer_tg_id != tg_user.id:
            is_subscribed_already, _ = await is_user_subscribed(
                message.bot, settings.channel_username, tg_user.id
            )

            referrer_user_id = get_user_id_by_tg_id(settings, referrer_tg_id)
            if referrer_user_id is not None:
                set_referrer(
                    settings,
                    referrer_user_id=referrer_user_id,
                    invited_user_id=user_id,
                    is_countable=not is_subscribed_already,
                )

    await message.answer(WELCOME, reply_markup=main_menu_keyboard())


@router.message(F.text == "Մասնակցել")
async def participate_handler(message: Message) -> None:
    settings = get_settings()
    await message.answer(
        PARTICIPATE_INFO,
        reply_markup=participate_keyboard(settings.channel_username),
    )


@router.callback_query(F.data == "check_participation")
async def check_participation_handler(query: CallbackQuery) -> None:
    if query.from_user is None:
        return

    settings = get_settings()
    tg_user = query.from_user
    user_id = get_user_id_by_tg_id(settings, tg_user.id)
    if user_id is None:
        user_id = create_user(
            settings,
            tg_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
        )
        ensure_status_row(settings, user_id)

    is_subscribed, check_error = await is_user_subscribed(
        query.bot, settings.channel_username, tg_user.id
    )
    if check_error is not None:
        await query.message.answer(CHECK_ERROR, reply_markup=main_menu_keyboard())
        await query.answer()
        return

    set_verified(settings, user_id, is_subscribed)

    if not is_subscribed:
        await query.message.answer(CHECK_FAIL, reply_markup=main_menu_keyboard())
        await query.answer()
        return

    verified_count, target, _eligible = recalc_referral_progress(settings, user_id)
    progress = f"{verified_count}/{target}"

    referrer_user_id = get_referrer_id(settings, user_id)
    if referrer_user_id is not None:
        recalc_referral_progress(settings, referrer_user_id)

    bot_user = await query.bot.get_me()
    ref_link = _build_ref_link(bot_user.username or "", tg_user.id)

    text = (
        f"{CHECK_OK}\n\n"
        f"{REF_LINK_TITLE}\n{ref_link}\n\n"
        f"📤 Կիսվիր ընկերների հետ և հավաքիր 3 հրավեր 🎯\n\n"
        f"{PROGRESS_TITLE} {progress}\n\n"
        f"{MAIN_MENU}"
    )

    await query.message.answer(
        text,
        reply_markup=referral_share_keyboard(ref_link),
    )
    await query.answer()


@router.callback_query(F.data == "winner_confirm_response")
async def winner_confirm_response_handler(query: CallbackQuery) -> None:
    if query.from_user is None:
        return

    settings = get_settings()
    winner_info = get_pending_winner_info(settings)
    if winner_info is None:
        await query.answer(WINNER_RESPONSE_INVALID, show_alert=True)
        return

    if winner_info["tg_id"] != query.from_user.id:
        await query.answer(WINNER_RESPONSE_INVALID, show_alert=True)
        return

    deadline_at = winner_info.get("response_deadline_at") or winner_info.get("deadline_at")
    if deadline_at is None or is_past_due(deadline_at):
        await query.answer(WINNER_RESPONSE_EXPIRED, show_alert=True)
        return

    responded_at = utcnow_iso()
    confirm_winner_response(
        settings,
        winner_id=winner_info["winner_id"],
        user_id=winner_info["user_id"],
        draw_id=winner_info["draw_id"],
        responded_at=responded_at,
    )
    await query.message.edit_reply_markup()
    await query.answer(WINNER_RESPONSE_CONFIRMED, show_alert=True)