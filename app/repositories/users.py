from typing import Optional

from config import Settings
from app.db.connection import get_connection


def create_user(
    settings: Settings,
    tg_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
) -> int:
    conn = get_connection(settings)
    try:
        cursor = conn.execute(
            """
            INSERT INTO users (tg_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(tg_id) DO NOTHING
            """,
            (tg_id, username, first_name, last_name),
        )
        conn.commit()
        if cursor.lastrowid:
            return int(cursor.lastrowid)
        row = conn.execute("SELECT id FROM users WHERE tg_id = ?", (tg_id,)).fetchone()
        return int(row["id"]) if row else 0
    finally:
        conn.close()


def get_user_id_by_tg_id(settings: Settings, tg_id: int) -> Optional[int]:
    conn = get_connection(settings)
    try:
        row = conn.execute("SELECT id FROM users WHERE tg_id = ?", (tg_id,)).fetchone()
        return int(row["id"]) if row else None
    finally:
        conn.close()


def get_tg_id_by_user_id(settings: Settings, user_id: int) -> Optional[int]:
    conn = get_connection(settings)
    try:
        row = conn.execute("SELECT tg_id FROM users WHERE id = ?", (user_id,)).fetchone()
        return int(row["tg_id"]) if row else None
    finally:
        conn.close()


def set_start_param(settings: Settings, user_id: int, start_param: str) -> None:
    conn = get_connection(settings)
    try:
        conn.execute(
            "UPDATE users SET start_param = ? WHERE id = ?",
            (start_param, user_id),
        )
        conn.commit()
    finally:
        conn.close()




