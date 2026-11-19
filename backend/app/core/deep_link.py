import re

_SOURCE_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def parse_source(args: str | None) -> str:
    if args and _SOURCE_RE.match(args):
        return args
    return "direct"
