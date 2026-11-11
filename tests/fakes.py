"""Test doubles for the ports of feedpaper's core."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import replace

from feedpaper.service import Article, FeedServiceError, Progress

from .conftest import PNG


class FakeService:
    """An in-memory feed service. Implements ``service.FeedService``.

    ``resolve`` swaps in the full text given in ``full_text`` (article id ->
    html). Set a ``fail_*`` attribute to make that step raise.
    """

    def __init__(self, articles: Sequence[Article] = (), full_text: dict[str, str] | None = None):
        self.unread = list(articles)
        self.full_text = full_text or {}
        self.resolved: list[str] = []
        self.marked: list[str] = []
        self.fail_verify = False
        self.fail_list = False
        self.fail_mark = False

    def verify(self) -> None:
        if self.fail_verify:
            raise FeedServiceError("wrong password")

    def feed_titles(self) -> list[str]:
        return sorted({a.feed_title for a in self.unread if a.feed_title}, key=str.lower)

    def list_unread(self) -> list[Article]:
        if self.fail_list:
            raise FeedServiceError("service is down")
        return list(self.unread)

    def resolve(
        self, articles: Sequence[Article], progress: Progress | None = None
    ) -> list[Article]:
        resolved = []
        for done, article in enumerate(articles, 1):
            self.resolved.append(article.id)
            if article.id in self.full_text:
                article = replace(article, html=self.full_text[article.id])
            resolved.append(article)
            if progress:
                progress(done, len(articles), article.title)
        return resolved

    def mark_as_read(self, articles: Iterable[Article]) -> None:
        if self.fail_mark:
            raise FeedServiceError("service is down")
        ids = [article.id for article in articles]
        self.marked.extend(ids)
        self.unread = [a for a in self.unread if a.id not in ids]


def fake_fetch_image(url: str) -> tuple[bytes, str] | None:
    """Stands in for the image download: every image is a tiny PNG."""
    return PNG, "image/png"
