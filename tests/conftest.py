from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import Settings
from app.db.init_db import init_db


@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    db_path = tmp_path / "test.sqlite3"
    test_settings = Settings(
        bot_token="test-token",
        channel_username="@domus_stores_test_1_test_1_test_1_test",
        admin_ids=[1],
        referral_target=3,
        winner_response_hours=48,
        db_path=str(db_path),
    )
    init_db(test_settings)
    return test_settings




