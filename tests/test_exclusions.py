import pytest

from feedpaper.exclusions import is_excluded, normalize_titles


def test_normalize_titles_strips_lowercases_and_drops_empty():
    titles = ["  Daring Fireball ", "HACKER Newsletter", "", "   ", None]

    assert normalize_titles(titles) == {"daring fireball", "hacker newsletter"}


def test_normalize_titles_collapses_duplicates():
    assert normalize_titles(["Blog", "blog", " BLOG "]) == {"blog"}


@pytest.mark.parametrize(
    ("feed_title", "expected"),
    [
        ("Daring Fireball", True),
        ("daring fireball", True),
        ("  DARING FIREBALL  ", True),
        ("Daring", False),
        ("Daring Fireball Linked List", False),
        ("", False),
        (None, False),
    ],
)
def test_is_excluded(feed_title, expected):
    excluded = normalize_titles(["Daring Fireball"])

    assert is_excluded(feed_title, excluded) is expected


def test_nothing_is_excluded_by_an_empty_set():
    assert is_excluded("Any Blog", normalize_titles([])) is False
