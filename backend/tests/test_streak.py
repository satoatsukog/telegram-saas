from datetime import timedelta

from app.core.streak import effective_streak
from app.core.timeutil import to_local, utcnow

TZ = "UTC"


def _today():
    return to_local(utcnow(), TZ).date()


def test_none_is_zero():
    assert effective_streak(5, None, TZ) == 0


def test_today_kept():
    assert effective_streak(5, _today(), TZ) == 5


def test_yesterday_kept():
    assert effective_streak(5, _today() - timedelta(days=1), TZ) == 5


def test_two_days_ago_resets_to_zero():
    assert effective_streak(5, _today() - timedelta(days=2), TZ) == 0


def test_older_resets_to_zero():
    assert effective_streak(9, _today() - timedelta(days=30), TZ) == 0
