from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

STEPS = ("start", "onboarding_done", "first_review_done", "paywall_view", "pay")


@dataclass
class Funnel:
    start: int = 0
    onboarding_done: int = 0
    first_review_done: int = 0
    paywall_view: int = 0
    pay: int = 0
    d1: int = 0
    d7: int = 0


def compute_funnel(
    events: list[tuple[int, str, str | None, datetime]],
    user_source: dict[int, str],
    now: datetime,
    days: int = 14,
) -> dict[str, Funnel]:
    since = now - timedelta(days=days)
    buckets: dict[tuple[str, str], set[int]] = defaultdict(set)
    for uid, event, source, ts in events:
        if ts < since:
            continue
        src = user_source.get(uid, "direct")
        if event in STEPS:
            buckets[(src, event)].add(uid)
        elif event == "review_day" and source in ("d1", "d7"):
            buckets[(src, source)].add(uid)
    result: dict[str, Funnel] = {}
    for src in sorted({s for s, _ in buckets}):
        n = lambda step: len(buckets.get((src, step), set()))
        result[src] = Funnel(n("start"), n("onboarding_done"), n("first_review_done"), n("paywall_view"), n("pay"), n("d1"), n("d7"))
    return result


def format_funnel(result: dict[str, Funnel], days: int = 14) -> str:
    if not result:
        return f"No events in the last {days} days."
    lines = [f"📊 Funnel — last {days} days (unique users per source)"]
    for src, f in result.items():
        lines.append(
            f"\n{src}\n"
            f"  start {f.start} → onboarding {f.onboarding_done} → "
            f"first review {f.first_review_done} → paywall {f.paywall_view} → pay {f.pay}\n"
            f"  retention: D1 {f.d1} · D7 {f.d7}"
        )
    return "\n".join(lines)
