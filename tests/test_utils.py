from src.utils import truncate


def test_truncate_short_string():
    assert truncate("hello", 10) == "hello"


def test_truncate_exact_length():
    assert truncate("hello", 5) == "hello"


def test_truncate_long_string():
    assert truncate("hello world", 8) == "hello..."


def test_truncate_very_small_maxlen():
    assert truncate("hello", 2) == "he"


def test_truncate_maxlen_three():
    assert truncate("hello", 3) == "hel"
