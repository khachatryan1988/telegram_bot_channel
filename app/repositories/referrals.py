from typing import Optional

from config import Settings
from app.db.connection import get_connection


def set_referrer(
        settings: Settings,
        referrer_user_id: int,
        invited_user_id: int,
        is_countable: bool = False,
) -> bool:
    if referrer_user_id == invited_user_id:
        return False

    conn = get_connection(settings)
    try:
        cursor = conn.execute(
            """
            INSERT INTO referrals (referrer_user_id, invited_user_id, is_countable)
            VALUES (?, ?, ?)
            ON CONFLICT(invited_user_id) DO NOTHING
            """,
            (referrer_user_id, invited_user_id, 1 if is_countable else 0),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_referrer_id(settings: Settings, invited_user_id: int) -> Optional[int]:
    conn = get_connection(settings)
    try:
        row = conn.execute(
            "SELECT referrer_user_id FROM referrals WHERE invited_user_id = ?",
            (invited_user_id,),
        ).fetchone()
        return int(row["referrer_user_id"]) if row else None
    finally:
        conn.close()


def get_verified_referral_count(settings: Settings, referrer_user_id: int) -> int:
    conn = get_connection(settings)
    try:
        row = conn.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM referrals r
            JOIN participant_status ps ON ps.user_id = r.invited_user_id
            WHERE r.referrer_user_id = ?
              AND r.is_countable = 1
              AND ps.is_verified = 1
            """,
            (referrer_user_id,),
        ).fetchone()
        return int(row["cnt"]) if row else 0
    finally:
        conn.close()


def get_all_referrals(settings: Settings) -> list[dict]:
    conn = get_connection(settings)
    try:
        rows = conn.execute(
            """
            SELECT
                r.referrer_user_id,
                ru.tg_id AS referrer_tg_id,
                ru.username AS referrer_username,
                ru.first_name AS referrer_first_name,
                ru.last_name AS referrer_last_name,

                r.invited_user_id,
                iu.tg_id AS invited_tg_id,
                iu.username AS invited_username,
                iu.first_name AS invited_first_name,
                iu.last_name AS invited_last_name,

                COALESCE(ps.is_verified, 0) AS is_verified,
                COALESCE(r.is_countable, 0) AS is_countable
            FROM referrals r
            LEFT JOIN users ru ON ru.id = r.referrer_user_id
            LEFT JOIN users iu ON iu.id = r.invited_user_id
            LEFT JOIN participant_status ps ON ps.user_id = r.invited_user_id
            ORDER BY r.referrer_user_id, r.invited_user_id
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_referrals_by_referrer_tg_id(settings: Settings, referrer_tg_id: int) -> list[dict]:
    conn = get_connection(settings)
    try:
        rows = conn.execute(
            """
            SELECT
                r.referrer_user_id,
                ru.tg_id AS referrer_tg_id,
                ru.username AS referrer_username,
                ru.first_name AS referrer_first_name,
                ru.last_name AS referrer_last_name,

                r.invited_user_id,
                iu.tg_id AS invited_tg_id,
                iu.username AS invited_username,
                iu.first_name AS invited_first_name,
                iu.last_name AS invited_last_name,

                COALESCE(ps.is_verified, 0) AS is_verified,
                COALESCE(r.is_countable, 0) AS is_countable
            FROM referrals r
            LEFT JOIN users ru ON ru.id = r.referrer_user_id
            LEFT JOIN users iu ON iu.id = r.invited_user_id
            LEFT JOIN participant_status ps ON ps.user_id = r.invited_user_id
            WHERE ru.tg_id = ?
            ORDER BY r.invited_user_id
            """,
            (referrer_tg_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_inviter_by_invited_tg_id(settings: Settings, invited_tg_id: int) -> Optional[dict]:
    conn = get_connection(settings)
    try:
        row = conn.execute(
            """
            SELECT
                r.referrer_user_id,
                ru.tg_id AS referrer_tg_id,
                ru.username AS referrer_username,
                ru.first_name AS referrer_first_name,
                ru.last_name AS referrer_last_name,

                r.invited_user_id,
                iu.tg_id AS invited_tg_id,
                iu.username AS invited_username,
                iu.first_name AS invited_first_name,
                iu.last_name AS invited_last_name,

                COALESCE(ps.is_verified, 0) AS is_verified,
                COALESCE(r.is_countable, 0) AS is_countable
            FROM referrals r
            LEFT JOIN users ru ON ru.id = r.referrer_user_id
            LEFT JOIN users iu ON iu.id = r.invited_user_id
            LEFT JOIN participant_status ps ON ps.user_id = r.invited_user_id
            WHERE iu.tg_id = ?
            LIMIT 1
            """,
            (invited_tg_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()