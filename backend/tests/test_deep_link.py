from app.core.deep_link import parse_source


def test_plain_source():
    assert parse_source("reels") == "reels"


def test_underscore_and_hyphen_allowed():
    assert parse_source("paid_chan-1") == "paid_chan-1"


def test_none_defaults_to_direct():
    assert parse_source(None) == "direct"


def test_empty_defaults_to_direct():
    assert parse_source("") == "direct"


def test_invalid_chars_default_to_direct():
    assert parse_source("bad source!") == "direct"


def test_too_long_defaults_to_direct():
    assert parse_source("x" * 65) == "direct"
