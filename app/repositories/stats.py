from config import Settings
from app.db.connection import get_connection


def get_total_users(settings: Settings) -> int:
    conn = get_connection(settings)
    try:
        row = conn.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()
        return int(row["cnt"]) if row else 0
    finally:
        conn.close()


def get_verified_users(settings: Settings) -> int:
    conn = get_connection(settings)
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM participant_status WHERE is_verified = 1"
        ).fetchone()
        return int(row["cnt"]) if row else 0
    finally:
        conn.close()


def get_eligible_users(settings: Settings) -> int:
    conn = get_connection(settings)
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM participant_status WHERE is_eligible = 1 AND is_expired = 0"
        ).fetchone()
        return int(row["cnt"]) if row else 0
    finally:
        conn.close()




