SPACE_SEPARATORS = (" - ", " — ", " – ")


def parse_line(line: str) -> tuple[str, str] | None:
    s = line.strip()
    if not s:
        return None
    candidates: list[tuple[int, int]] = []
    for sep in SPACE_SEPARATORS:
        i = s.find(sep)
        if i != -1:
            candidates.append((i, len(sep)))
    colon = s.find(":")
    if colon != -1:
        candidates.append((colon, 1))
    if not candidates:
        return None
    pos, length = min(candidates, key=lambda c: c[0])
    front = s[:pos].strip()
    back = s[pos + length:].strip()
    if not front or not back:
        return None
    return front, back


def parse_list(text: str) -> list[tuple[str, str]]:
    pairs = []
    for line in text.splitlines():
        pair = parse_line(line)
        if pair is not None:
            pairs.append(pair)
    return pairs
