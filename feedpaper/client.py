from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class ClientError(Exception):
    """Raised when a feed service cannot answer a request."""


@dataclass(frozen=True)
class Article:
    """One unread post, resolved and ready to render.

    ``html`` is the final content: the client has already chosen between the
    inline content, a full-text extraction, or whatever else its service
    offers. ``id`` is service-local and opaque to everyone but the client that
    handed it out.
    """

    id: str
    title: str
    html: str
    feed_title: str
    url: str | None = None
    author: str | None = None
    published: datetime | None = None


# Called once with ``done=0`` as soon as the total is known, then once per
# article as it is resolved: progress(done, total, title).
Progress = Callable[[int, int, str], None]


class Client(Protocol):
    """What feedpaper needs from a feed service.

    Implementations keep their service's quirks to themselves and raise
    ``ClientError`` (or a subclass) when a request fails.
    """

    def verify(self) -> None:
        """Check the credentials and raise when they don't work."""

    def feed_titles(self) -> list[str]:
        """Titles of the subscribed blogs, sorted case-insensitively."""

    def fetch_unread(self, progress: Progress | None = None) -> list[Article]:
        """Every unread post, with its content resolved."""

    def mark_as_read(self, articles: Iterable[Article]) -> None:
        """Mark the given articles as read on the service."""
