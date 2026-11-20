from datetime import date, timedelta

from app.core.timeutil import to_local, utcnow


def effective_streak(streak: int, last_review_on: date | None, tz: str) -> int:
    if last_review_on is None:
        return 0
    today = to_local(utcnow(), tz).date()
    if last_review_on < today - timedelta(days=1):
        return 0
    return streak
