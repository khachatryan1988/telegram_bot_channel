from config import Settings
from app.db.connection import get_connection


def log_action(
    settings: Settings,
    action: str,
    user_id: int | None = None,
    meta_json: str | None = None,
) -> None:
    conn = get_connection(settings)
    try:
        conn.execute(
            """
            INSERT INTO audit_logs (user_id, action, meta_json)
            VALUES (?, ?, ?)
            """,
            (user_id, action, meta_json),
        )
        conn.commit()
    finally:
        conn.close()




