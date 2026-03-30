from config import Settings
from app.db.connection import get_connection


def remember_update_id(settings: Settings, update_id: int) -> bool:
    conn = get_connection(settings)
    try:
        cursor = conn.execute(
            """
            INSERT INTO processed_updates (update_id)
            VALUES (?)
            ON CONFLICT(update_id) DO NOTHING
            """,
            (update_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()




