import sqlite3

from app.db.connection import get_connection
from app.repositories.draws import create_draw, get_active_draw, update_draw_status
from app.repositories.processed_updates import remember_update_id
from app.repositories.referrals import get_referrer_id, set_referrer
from app.repositories.stats import get_total_users
from app.repositories.status import ensure_status_row, set_eligible, set_verified
from app.repositories.users import (
    create_user,
    get_tg_id_by_user_id,
    get_user_id_by_tg_id,
    set_start_param,
)
from app.repositories.winners import create_winner, get_active_winner_info, update_winner_status
from app.services.draw import confirm_winner_response


def test_db_schema_is_initialized(settings) -> None:
    conn = sqlite3.connect(settings.db_path)
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
    finally:
        conn.close()

    assert {
        "users",
        "referrals",
        "participant_status",
        "draws",
        "winners",
        "processed_updates",
    }.issubset(
        tables
    )


def test_user_and_referral_repositories_smoke(settings) -> None:
    referrer_id = create_user(settings, 500, "referrer", "Ref", None)
    invited_id = create_user(settings, 501, "invited", "Inv", None)
    ensure_status_row(settings, referrer_id)
    ensure_status_row(settings, invited_id)

    set_start_param(settings, invited_id, "ref_500")
    assert set_referrer(settings, referrer_id, invited_id) is True
    set_verified(settings, invited_id, True)
    set_eligible(settings, referrer_id, False)

    assert get_total_users(settings) == 2
    assert get_user_id_by_tg_id(settings, 500) == referrer_id
    assert get_tg_id_by_user_id(settings, invited_id) == 501
    assert get_referrer_id(settings, invited_id) == referrer_id


def test_draw_and_winner_repositories_smoke(settings) -> None:
    user_id = create_user(settings, 600, "winner", "Win", None)
    ensure_status_row(settings, user_id)

    draw_id = create_draw(
        settings,
        status="active",
        winner_user_id=user_id,
        deadline_at="2025-01-01T00:00:00+00:00",
    )
    winner_id = create_winner(
        settings,
        draw_id=draw_id,
        user_id=user_id,
        status="pending_response",
        winner_notified_at="2024-12-30T00:00:00+00:00",
        response_deadline_at="2025-01-01T00:00:00+00:00",
    )

    winner_info = get_active_winner_info(settings)

    assert winner_id > 0
    assert winner_info is not None
    assert winner_info["winner_id"] == winner_id
    assert winner_info["response_deadline_at"] == "2025-01-01T00:00:00+00:00"

    update_draw_status(settings, draw_id, "expired")
    assert get_active_draw(settings) is None


def test_database_connection_returns_row_objects(settings) -> None:
    conn = get_connection(settings)
    try:
        row = conn.execute("SELECT 1 AS value").fetchone()
    finally:
        conn.close()

    assert row["value"] == 1


def test_confirm_winner_response_completes_draw(settings) -> None:
    user_id = create_user(settings, 700, "winner2", "Win2", None)
    ensure_status_row(settings, user_id)
    draw_id = create_draw(
        settings,
        status="active",
        winner_user_id=user_id,
        deadline_at="2025-01-01T00:00:00+00:00",
    )
    winner_id = create_winner(
        settings,
        draw_id=draw_id,
        user_id=user_id,
        status="pending_response",
        winner_notified_at="2024-12-30T00:00:00+00:00",
        response_deadline_at="2025-01-01T00:00:00+00:00",
    )

    confirm_winner_response(
        settings,
        winner_id=winner_id,
        user_id=user_id,
        draw_id=draw_id,
        responded_at="2024-12-30T12:00:00+00:00",
    )

    assert get_active_draw(settings) is None
    winner_info = get_active_winner_info(settings)
    assert winner_info is not None
    assert winner_info["status"] == "responded"
    assert winner_info["responded_at"] == "2024-12-30T12:00:00+00:00"


def test_update_winner_status_preserves_existing_timestamps(settings) -> None:
    user_id = create_user(settings, 800, "winner3", "Win3", None)
    ensure_status_row(settings, user_id)
    draw_id = create_draw(
        settings,
        status="active",
        winner_user_id=user_id,
        deadline_at="2025-01-01T00:00:00+00:00",
    )
    winner_id = create_winner(
        settings,
        draw_id=draw_id,
        user_id=user_id,
        status="pending_response",
        winner_notified_at="2024-12-30T00:00:00+00:00",
        response_deadline_at="2025-01-01T00:00:00+00:00",
    )

    update_winner_status(
        settings,
        winner_id=winner_id,
        status="responded",
        responded_at="2024-12-30T12:00:00+00:00",
    )
    update_winner_status(
        settings,
        winner_id=winner_id,
        status="responded",
    )

    conn = get_connection(settings)
    try:
        row = conn.execute(
            "SELECT responded_at, expired_at FROM winners WHERE id = ?",
            (winner_id,),
        ).fetchone()
    finally:
        conn.close()

    assert row["responded_at"] == "2024-12-30T12:00:00+00:00"
    assert row["expired_at"] is None


def test_processed_updates_are_idempotent(settings) -> None:
    assert remember_update_id(settings, 12345) is True
    assert remember_update_id(settings, 12345) is False




