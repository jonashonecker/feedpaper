from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable


class FeedServiceError(Exception):
    """Raised when a feed service cannot answer a request."""


@dataclass(frozen=True)
class Article:
    """One unread post.

    ``html`` is the best content known so far: what the service returned in
    bulk after ``list_unread``, and the final content after ``resolve``. ``id``
    is service-local and opaque to everyone but the adapter that handed it out.
    """

    id: str
    title: str
    html: str
    feed_title: str
    url: str | None = None
    author: str | None = None
    published: datetime | None = None


# Called once per article as ``resolve`` finishes it: progress(done, total, title).
Progress = Callable[[int, int, str], None]


@runtime_checkable
class FeedService(Protocol):
    """What feedpaper needs from a feed service.

    Fetching is split in two steps, so feedpaper can drop the posts it won't
    use before an adapter spends requests on their content:

    1. ``list_unread`` returns every unread post with the content the service
       hands out in bulk, which is cheap.
    2. ``resolve`` replaces that content with the best version the service can
       offer, such as a full-text extraction. A service without a better source
       returns the articles unchanged.

    Implementations keep their service's quirks to themselves and raise
    ``FeedServiceError`` (or a subclass) when a request fails.
    """

    def verify(self) -> None:
        """Check the credentials and raise when they don't work."""
        ...

    def feed_titles(self) -> list[str]:
        """Titles of the subscribed blogs, sorted case-insensitively."""
        ...

    def list_unread(self) -> list[Article]:
        """Every unread post, with the content the service returns in bulk."""
        ...

    def resolve(
        self, articles: Sequence[Article], progress: Progress | None = None
    ) -> list[Article]:
        """The same articles in the same order, each with its best content.

        Only ``html`` may differ from the input.
        """
        ...

    def mark_as_read(self, articles: Iterable[Article]) -> None:
        """Mark the given articles as read on the service."""
        ...
