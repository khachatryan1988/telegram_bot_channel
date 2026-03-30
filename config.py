from __future__ import annotations


from dataclasses import dataclass

from dotenv import load_dotenv
import os

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def _parse_int(value: str, name: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


@dataclass(frozen=True)
class Settings:
    bot_token: str
    channel_username: str
    admin_ids: list[int]
    referral_target: int
    winner_response_hours: int
    db_path: str


def get_settings() -> Settings:
    load_dotenv()

    bot_token = _require_env("BOT_TOKEN")
    channel_username = _require_env("CHANNEL_USERNAME")
    admin_ids_raw = _require_env("ADMIN_IDS")
    admin_ids = [int(x) for x in admin_ids_raw.split(",") if x.strip().isdigit()]
    if not admin_ids:
        raise RuntimeError("ADMIN_IDS must contain at least one numeric ID")

    referral_target = _parse_int(_require_env("REFERRAL_TARGET"), "REFERRAL_TARGET")
    winner_response_hours = _parse_int(
        _require_env("WINNER_RESPONSE_HOURS"), "WINNER_RESPONSE_HOURS"
    )
    db_path = _require_env("DB_PATH")

    return Settings(
        bot_token=bot_token,
        channel_username=channel_username,
        admin_ids=admin_ids,
        referral_target=referral_target,
        winner_response_hours=winner_response_hours,
        db_path=db_path,
    )




