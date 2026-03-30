from pathlib import Path
import sqlite3

from config import Settings


def _ensure_winners_columns(conn: sqlite3.Connection) -> None:
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(winners)").fetchall()
    }

    if "winner_notified_at" not in columns:
        conn.execute("ALTER TABLE winners ADD COLUMN winner_notified_at TEXT")
        if "notified_at" in columns:
            conn.execute(
                "UPDATE winners SET winner_notified_at = notified_at "
                "WHERE winner_notified_at IS NULL"
            )

    if "response_deadline_at" not in columns:
        conn.execute("ALTER TABLE winners ADD COLUMN response_deadline_at TEXT")
        conn.execute(
            """
            UPDATE winners
            SET response_deadline_at = (
                SELECT deadline_at
                FROM draws
                WHERE draws.id = winners.draw_id
            )
            WHERE response_deadline_at IS NULL
            """
        )


def init_db(settings: Settings) -> None:
    conn = sqlite3.connect(settings.db_path)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        schema_path = Path(__file__).with_name("schema.sql")
        schema_sql = schema_path.read_text(encoding="utf-8")
        conn.executescript(schema_sql)
        _ensure_winners_columns(conn)
        conn.commit()
    finally:
        conn.close()




