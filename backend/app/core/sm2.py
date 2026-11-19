from dataclasses import dataclass

GRADES = {"again": 2, "good": 4, "easy": 5}
MIN_EASE = 1.3


@dataclass(frozen=True)
class SchedulingState:
    ease: float = 2.5
    interval: int = 0
    repetitions: int = 0


def schedule(state: SchedulingState, grade: str) -> SchedulingState:
    q = GRADES[grade]
    ease = max(MIN_EASE, state.ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    if q < 3:
        return SchedulingState(ease=ease, interval=1, repetitions=0)
    repetitions = state.repetitions + 1
    if repetitions == 1:
        interval = 1
    elif repetitions == 2:
        interval = 6
    else:
        interval = round(state.interval * ease)
    return SchedulingState(ease=ease, interval=interval, repetitions=repetitions)
