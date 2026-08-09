from __future__ import annotations

from pathlib import Path

DEFAULT_EXCLUDE_FILE = "excluded_feeds.txt"


def load_excluded_titles(path, extra=None) -> set[str]:
    """Collect excluded feed titles from a file plus optional extra titles.

    File format: one feed title per line; blank lines and lines starting
    with ``#`` are ignored. Matching is case-insensitive, so all titles are
    returned lower-cased.
    """
    titles: set[str] = set()

    p = Path(path)
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            titles.add(line.lower())

    for title in extra or []:
        cleaned = title.strip()
        if cleaned:
            titles.add(cleaned.lower())

    return titles


def is_excluded(feed_title, excluded_titles) -> bool:
    """True if the given feed title is in the excluded set (case-insensitive)."""
    return bool(feed_title) and feed_title.strip().lower() in excluded_titles
