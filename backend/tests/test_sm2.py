from app.core.sm2 import SchedulingState, schedule


def test_first_good():
    s = schedule(SchedulingState(), "good")
    assert s.repetitions == 1
    assert s.interval == 1
    assert round(s.ease, 2) == 2.5


def test_second_good():
    s = schedule(SchedulingState(ease=2.5, interval=1, repetitions=1), "good")
    assert s.repetitions == 2
    assert s.interval == 6


def test_third_good_uses_ease():
    s = schedule(SchedulingState(ease=2.5, interval=6, repetitions=2), "good")
    assert s.repetitions == 3
    assert s.interval == 15


def test_easy_raises_ease_and_counts():
    s = schedule(SchedulingState(), "easy")
    assert s.ease > 2.5
    assert s.interval == 1
    assert s.repetitions == 1


def test_again_is_lapse():
    s = schedule(SchedulingState(ease=2.5, interval=15, repetitions=3), "again")
    assert s.repetitions == 0
    assert s.interval == 1
    assert s.ease < 2.5
    assert s.ease >= 1.3


def test_ease_never_below_floor():
    s = SchedulingState(ease=1.3, interval=1, repetitions=0)
    for _ in range(5):
        s = schedule(s, "again")
    assert s.ease >= 1.3
