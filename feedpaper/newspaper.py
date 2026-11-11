"""Building a newspaper: feedpaper's core use case.

``build_newspaper`` is what a user interface calls. It reaches the outside
world only through what it's given: a ``FeedService`` for the posts, a
``fetch_image`` function for their images and a ``Reporter`` for progress.
It never prints and knows nothing about the command line.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from feedpaper.exclusions import is_excluded, normalize_titles
from feedpaper.render import ImageFetcher, http_fetch_image, render_epub
from feedpaper.service import Article, FeedService, FeedServiceError


class Reporter:
    """Hears about each step as it happens. The default hears nothing.

    A user interface subclasses this to show progress while a newspaper is
    being built; everything else it needs is in the ``Newspaper`` returned.
    """

    def found(self, count: int) -> None:
        """The service has ``count`` unread posts."""

    def excluded(self, count: int, feed_titles: list[str]) -> None:
        """``count`` posts from these blogs are left out and stay unread."""

    def resolving(self, count: int) -> None:
        """About to fetch the full content of ``count`` posts."""

    def resolved(self, done: int, total: int, title: str) -> None:
        """Post ``done`` of ``total`` has its full content."""

    def rendering(self) -> None:
        """About to write the ePub."""


@dataclass(frozen=True)
class Newspaper:
    """What ``build_newspaper`` did."""

    found: int
    """Unread posts on the service."""
    excluded: int
    """Posts left out because their blog is excluded. They stay unread."""
    articles: tuple[Article, ...] = ()
    """The posts in the newspaper."""
    path: Path | None = None
    """The ePub written, or None when there was nothing to build."""
    marked_read: bool = False
    """Whether the posts in the newspaper were marked as read."""
    mark_error: FeedServiceError | None = None
    """Why marking as read failed, if it did. The ePub exists regardless."""


def build_newspaper(
    service: FeedService,
    out_dir: str | Path,
    *,
    excluded_blogs: Iterable[str] = (),
    keep_unread: bool = False,
    reporter: Reporter | None = None,
    fetch_image: ImageFetcher = http_fetch_image,
    today: date | None = None,
) -> Newspaper:
    """Turn the service's unread posts into an ePub in ``out_dir``.

    Posts from ``excluded_blogs`` are left out before any full content is
    fetched, and are never marked as read. The posts in the newspaper are
    marked as read once the ePub is written, unless ``keep_unread`` is set. If
    marking fails, the ePub stays and the error is in the result.

    Raises ``FeedServiceError`` when the posts can't be fetched.
    """
    reporter = reporter or Reporter()

    unread = service.list_unread()
    reporter.found(len(unread))
    if not unread:
        return Newspaper(found=0, excluded=0)

    excluded_titles = normalize_titles(excluded_blogs)
    included = [a for a in unread if not is_excluded(a.feed_title, excluded_titles)]
    left_out = [a for a in unread if is_excluded(a.feed_title, excluded_titles)]
    if left_out:
        reporter.excluded(
            len(left_out), sorted({a.feed_title for a in left_out if a.feed_title})
        )
    if not included:
        return Newspaper(found=len(unread), excluded=len(left_out))

    reporter.resolving(len(included))
    articles = service.resolve(included, progress=reporter.resolved)

    reporter.rendering()
    path = render_epub(articles, out_dir, fetch_image=fetch_image, today=today)

    marked_read, mark_error = False, None
    if not keep_unread:
        try:
            service.mark_as_read(articles)
            marked_read = True
        except FeedServiceError as exc:
            mark_error = exc

    return Newspaper(
        found=len(unread),
        excluded=len(left_out),
        articles=tuple(articles),
        path=path,
        marked_read=marked_read,
        mark_error=mark_error,
    )
