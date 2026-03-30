from typing import Optional

from config import Settings
from app.db.connection import get_connection


def set_referrer(
    settings: Settings,
    referrer_user_id: int,
    invited_user_id: int,
) -> bool:
    if referrer_user_id == invited_user_id:
        return False

    conn = get_connection(settings)
    try:
        cursor = conn.execute(
            """
            INSERT INTO referrals (referrer_user_id, invited_user_id)
            VALUES (?, ?)
            ON CONFLICT(invited_user_id) DO NOTHING
            """,
            (referrer_user_id, invited_user_id),
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
            WHERE r.referrer_user_id = ? AND ps.is_verified = 1
            """,
            (referrer_user_id,),
        ).fetchone()
        return int(row["cnt"]) if row else 0
    finally:
        conn.close()




