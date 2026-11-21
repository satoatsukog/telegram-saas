from datetime import timedelta

from app.core.stats import compute_funnel, format_funnel
from app.core.timeutil import utcnow

NOW = utcnow()


def ev(uid, event, source=None, days_ago=0):
    return (uid, event, source, NOW - timedelta(days=days_ago))


def test_funnel_counts_unique_users_per_source():
    events = [
        ev(1, "start"),
        ev(1, "start"),
        ev(1, "onboarding_done"),
        ev(1, "first_review_done"),
        ev(2, "start"),
        ev(3, "start"),
        ev(3, "onboarding_done"),
    ]
    source = {1: "aud_ielts", 2: "aud_ielts", 3: "aud_med"}
    result = compute_funnel(events, source, NOW)
    assert result["aud_ielts"].start == 2
    assert result["aud_ielts"].onboarding_done == 1
    assert result["aud_ielts"].first_review_done == 1
    assert result["aud_med"].start == 1
    assert result["aud_med"].onboarding_done == 1


def test_funnel_excludes_events_outside_window():
    events = [ev(1, "start", days_ago=20), ev(2, "start", days_ago=3)]
    result = compute_funnel(events, {1: "tt", 2: "tt"}, NOW, days=14)
    assert result["tt"].start == 1


def test_funnel_retention_from_review_day():
    events = [
        ev(1, "start"),
        ev(1, "review_day", source="d1"),
        ev(1, "review_day", source="d7"),
        ev(2, "review_day", source="d1"),
    ]
    result = compute_funnel(events, {1: "reels", 2: "reels"}, NOW)
    assert result["reels"].d1 == 2
    assert result["reels"].d7 == 1


def test_funnel_defaults_unknown_source_to_direct():
    result = compute_funnel([ev(9, "start"), ev(9, "pay")], {}, NOW)
    assert result["direct"].start == 1
    assert result["direct"].pay == 1


def test_format_funnel_empty():
    assert "No events" in format_funnel({}, days=14)


def test_format_funnel_includes_source_and_stages():
    result = compute_funnel([ev(1, "start"), ev(1, "pay")], {1: "aud_polish"}, NOW)
    text = format_funnel(result)
    assert "aud_polish" in text
    assert "pay 1" in text
