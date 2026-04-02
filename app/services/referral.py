from config import Settings
from app.repositories.referrals import get_verified_referral_count
from app.repositories.status import set_eligible
from app.db.connection import get_connection


def recalc_referral_progress(settings: Settings, user_id: int) -> tuple[int, int, bool]:
    count = get_verified_referral_count(settings, user_id)
    target = settings.referral_target
    eligible = count >= target
    set_eligible(settings, user_id, eligible)
    return count, target, eligible

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



