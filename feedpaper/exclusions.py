from __future__ import annotations


def normalize_titles(titles) -> set[str]:
    """Return a set of stripped, lower-cased, non-empty titles."""
    return {t.strip().lower() for t in titles if t and t.strip()}


def is_excluded(feed_title, excluded_titles) -> bool:
    """True if the given feed title is in the excluded set (case-insensitive)."""
    return bool(feed_title) and feed_title.strip().lower() in excluded_titles
