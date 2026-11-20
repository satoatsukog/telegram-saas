from datetime import datetime, timedelta

PLAN_DAYS = {"monthly": 30, "yearly": 365}


def is_premium(premium_until: datetime | None, now: datetime) -> bool:
    return premium_until is not None and premium_until > now


def extend(premium_until: datetime | None, now: datetime, days: int) -> datetime:
    base = premium_until if premium_until and premium_until > now else now
    return base + timedelta(days=days)


def shorten(premium_until: datetime | None, now: datetime, days: int) -> datetime | None:
    if premium_until is None:
        return None
    reduced = premium_until - timedelta(days=days)
    return reduced if reduced > now else now
