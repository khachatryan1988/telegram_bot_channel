from typing import Optional

from config import Settings
from app.db.connection import get_connection


def create_draw(
    settings: Settings,
    status: str,
    winner_user_id: int | None,
    deadline_at: str | None,
) -> int:
    conn = get_connection(settings)
    try:
        cursor = conn.execute(
            """
            INSERT INTO draws (status, winner_user_id, deadline_at)
            VALUES (?, ?, ?)
            """,
            (status, winner_user_id, deadline_at),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def update_draw_status(settings: Settings, draw_id: int, status: str) -> None:
    conn = get_connection(settings)
    try:
        conn.execute("UPDATE draws SET status = ? WHERE id = ?", (status, draw_id))
        conn.commit()
    finally:
        conn.close()


def get_active_draw(settings: Settings) -> Optional[dict]:
    conn = get_connection(settings)
    try:
        row = conn.execute(
            "SELECT * FROM draws WHERE status = 'active' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()




