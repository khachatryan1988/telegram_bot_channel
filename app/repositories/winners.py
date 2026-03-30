from typing import Optional

from config import Settings
from app.db.connection import get_connection

_UNSET = object()


def create_winner(
    settings: Settings,
    draw_id: int,
    user_id: int,
    status: str,
    winner_notified_at: str | None,
    response_deadline_at: str | None,
) -> int:
    conn = get_connection(settings)
    try:
        cursor = conn.execute(
            """
            INSERT INTO winners (
                draw_id, user_id, status, winner_notified_at, response_deadline_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (draw_id, user_id, status, winner_notified_at, response_deadline_at),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def update_winner_status(
    settings: Settings,
    winner_id: int,
    status: str,
    responded_at: str | None | object = _UNSET,
    expired_at: str | None | object = _UNSET,
) -> None:
    conn = get_connection(settings)
    try:
        fields = ["status = ?"]
        params: list[object] = [status]

        if responded_at is not _UNSET:
            fields.append("responded_at = ?")
            params.append(responded_at)

        if expired_at is not _UNSET:
            fields.append("expired_at = ?")
            params.append(expired_at)

        params.append(winner_id)
        conn.execute(
            f"UPDATE winners SET {', '.join(fields)} WHERE id = ?",
            params,
        )
        conn.commit()
    finally:
        conn.close()


def get_pending_winner_info(settings: Settings) -> Optional[dict]:
    conn = get_connection(settings)
    try:
        row = conn.execute(
            """
            SELECT w.id AS winner_id, w.user_id, w.response_deadline_at,
                   d.id AS draw_id, d.deadline_at, u.tg_id, u.username,
                   u.first_name, u.last_name
            FROM winners w
            JOIN draws d ON d.id = w.draw_id
            JOIN users u ON u.id = w.user_id
            WHERE d.status = 'active' AND w.status = 'pending_response'
            ORDER BY w.id DESC
            LIMIT 1
            """
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_active_winner_info(settings: Settings) -> Optional[dict]:
    conn = get_connection(settings)
    try:
        row = conn.execute(
            """
            SELECT w.id AS winner_id, w.user_id, w.status, w.winner_notified_at,
                   w.response_deadline_at, w.responded_at, d.id AS draw_id,
                   d.deadline_at, u.tg_id, u.username, u.first_name, u.last_name
            FROM winners w
            JOIN draws d ON d.id = w.draw_id
            JOIN users u ON u.id = w.user_id
            WHERE d.status IN ('active', 'completed')
            ORDER BY w.id DESC
            LIMIT 1
            """
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()




