from datetime import datetime, timedelta, timezone


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def add_hours_iso(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).replace(
        microsecond=0
    ).isoformat()


def parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def is_past_due(value: str) -> bool:
    return parse_iso_datetime(value) <= datetime.now(timezone.utc)




