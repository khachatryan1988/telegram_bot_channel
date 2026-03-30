from typing import Iterable

from config import Settings
from app.db.connection import get_connection


def ensure_status_row(settings: Settings, user_id: int) -> None:
    conn = get_connection(settings)
    try:
        conn.execute(
            """
            INSERT INTO participant_status (user_id)
            VALUES (?)
            ON CONFLICT(user_id) DO NOTHING
            """,
            (user_id,),
        )
        conn.commit()
    finally:
        conn.close()


def set_verified(settings: Settings, user_id: int, is_verified: bool) -> None:
    conn = get_connection(settings)
    try:
        conn.execute(
            """
            INSERT INTO participant_status (user_id, is_verified, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                is_verified = excluded.is_verified,
                updated_at = datetime('now')
            """,
            (user_id, int(is_verified)),
        )
        conn.commit()
    finally:
        conn.close()


def set_eligible(settings: Settings, user_id: int, is_eligible: bool) -> None:
    conn = get_connection(settings)
    try:
        conn.execute(
            """
            INSERT INTO participant_status (user_id, is_eligible, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                is_eligible = excluded.is_eligible,
                updated_at = datetime('now')
            """,
            (user_id, int(is_eligible)),
        )
        conn.commit()
    finally:
        conn.close()


def set_winner(settings: Settings, user_id: int, is_winner: bool) -> None:
    conn = get_connection(settings)
    try:
        conn.execute(
            """
            INSERT INTO participant_status (user_id, is_winner, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                is_winner = excluded.is_winner,
                updated_at = datetime('now')
            """,
            (user_id, int(is_winner)),
        )
        conn.commit()
    finally:
        conn.close()


def set_expired(settings: Settings, user_id: int, is_expired: bool) -> None:
    conn = get_connection(settings)
    try:
        conn.execute(
            """
            INSERT INTO participant_status (user_id, is_expired, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                is_expired = excluded.is_expired,
                updated_at = datetime('now')
            """,
            (user_id, int(is_expired)),
        )
        conn.commit()
    finally:
        conn.close()


def get_eligible_user_ids(settings: Settings) -> list[int]:
    conn = get_connection(settings)
    try:
        rows = conn.execute(
            """
            SELECT user_id FROM participant_status
            WHERE is_eligible = 1 AND is_expired = 0
            """
        ).fetchall()
        return [int(row["user_id"]) for row in rows]
    finally:
        conn.close()




