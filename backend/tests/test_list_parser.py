from app.core.list_parser import parse_line, parse_list


def test_hyphen_inside_word_not_split():
    assert parse_line("well-known - famous") == ("well-known", "famous")


def test_emdash_with_hyphenated_word():
    assert parse_line("self-esteem — confidence") == ("self-esteem", "confidence")


def test_first_colon_keeps_rest():
    assert parse_line("ratio: a:b relation") == ("ratio", "a:b relation")


def test_endash_separator():
    assert parse_line("fast – quick") == ("fast", "quick")


def test_bare_hyphenated_token_is_skipped():
    assert parse_line("state-of-the-art") is None


def test_earliest_separator_wins():
    assert parse_line("foo - bar: baz") == ("foo", "bar: baz")


def test_parse_list_skips_blank_and_unparseable():
    text = "\nword\nubiquitous - everywhere\n   \nmitigate: lessen\n"
    assert parse_list(text) == [("ubiquitous", "everywhere"), ("mitigate", "lessen")]
