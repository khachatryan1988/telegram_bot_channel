import json
import random
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from config import Settings
from texts import WINNER_NOTIFY
from app.repositories.draws import create_draw, get_active_draw, update_draw_status
from app.repositories.audit_logs import log_action
from app.repositories.status import get_eligible_user_ids, set_expired, set_winner
from app.repositories.winners import (
    create_winner,
    get_pending_winner_info,
    update_winner_status,
)
from app.keyboards.main import winner_response_keyboard
from app.repositories.users import get_tg_id_by_user_id
from app.services.verification import is_user_subscribed
from app.utils.time import add_hours_iso, is_past_due, utcnow_iso
from app.db.connection import get_connection


def _pick_candidate(candidates: list[int]) -> list[int]:
    pool = candidates[:]
    random.shuffle(pool)
    return pool


async def draw_winner(bot: Bot, settings: Settings) -> Optional[dict]:
    active = get_active_draw(settings)
    if active is not None:
        return None

    eligible_user_ids = get_eligible_user_ids(settings)
    if not eligible_user_ids:
        return None

    for user_id in _pick_candidate(eligible_user_ids):
        tg_id = get_tg_id_by_user_id(settings, user_id)
        if tg_id is None:
            continue
        is_member, err = await is_user_subscribed(
            bot, settings.channel_username, tg_id
        )
        if err is not None:
            return None
        if not is_member:
            continue

        deadline_at = add_hours_iso(settings.winner_response_hours)
        draw_id = create_draw(
            settings, status="active", winner_user_id=user_id, deadline_at=deadline_at
        )
        winner_id = create_winner(
            settings,
            draw_id=draw_id,
            user_id=user_id,
            status="pending_response",
            winner_notified_at=utcnow_iso(),
            response_deadline_at=deadline_at,
        )
        set_winner(settings, user_id, True)
        set_expired(settings, user_id, False)

        try:
            await bot.send_message(
                tg_id,
                WINNER_NOTIFY,
                reply_markup=winner_response_keyboard(),
            )
        except TelegramAPIError:
            update_winner_status(
                settings,
                winner_id=winner_id,
                status="expired",
                expired_at=utcnow_iso(),
            )
            set_winner(settings, user_id, False)
            set_expired(settings, user_id, True)
            update_draw_status(settings, draw_id, "expired")
            continue
        conn = get_connection(settings)
        row = conn.execute(
       "SELECT username, first_name, last_name FROM users WHERE id = ?",
    (user_id,),
        ).fetchone()
        conn.close()

        username = row["username"] if row else None
        first_name = row["first_name"] if row else None
        last_name = row["last_name"] if row else None

        result = {
            "draw_id": draw_id,
            "winner_id": winner_id,
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "deadline_at": deadline_at,
        }
        log_action(
            settings,
            action="draw_winner",
            user_id=user_id,
            meta_json=json.dumps({"draw_id": draw_id, "winner_id": winner_id}),
        )
        return result

    return None


async def redraw_winner(bot: Bot, settings: Settings) -> Optional[dict]:
    active_winner = get_pending_winner_info(settings)
    if active_winner is not None:
        deadline_at = active_winner.get("response_deadline_at") or active_winner.get(
            "deadline_at"
        )
        if deadline_at is None or not is_past_due(deadline_at):
            return None

        update_winner_status(
            settings,
            winner_id=active_winner["winner_id"],
            status="redrawn",
            expired_at=utcnow_iso(),
        )
        set_winner(settings, active_winner["user_id"], False)
        set_expired(settings, active_winner["user_id"], True)

        draw_id = active_winner["draw_id"]
        update_draw_status(settings, draw_id, "expired")
        log_action(
            settings,
            action="redraw_expire",
            user_id=active_winner["user_id"],
            meta_json=json.dumps(
                {"draw_id": draw_id, "winner_id": active_winner["winner_id"]}
            ),
        )

    result = await draw_winner(bot, settings)
    if result is not None:
        log_action(
            settings,
            action="redraw_winner",
            user_id=result["user_id"],
            meta_json=json.dumps(
                {"draw_id": result["draw_id"], "winner_id": result["winner_id"]}
            ),
        )
    return result


def confirm_winner_response(
    settings: Settings,
    winner_id: int,
    user_id: int,
    draw_id: int,
    responded_at: str,
) -> None:
    update_winner_status(
        settings,
        winner_id=winner_id,
        status="responded",
        responded_at=responded_at,
    )
    update_draw_status(settings, draw_id, "completed")
    log_action(
        settings,
        action="winner_responded",
        user_id=user_id,
        meta_json=json.dumps({"draw_id": draw_id, "winner_id": winner_id}),
    )




