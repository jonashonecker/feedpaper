from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import replace
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from feedpaper.client import Article, ClientError, Progress

API_BASE = "https://api.feedbin.com/v2"
ENTRIES_CHUNK = 100  # max ids per /entries.json request
UNREAD_CHUNK = 1000  # max ids per mark-as-read request
DEFAULT_TIMEOUT = 30

# Markers that suggest a feed only delivered a truncated teaser.
_TRUNCATION_MARKERS = (
    "read more",
    "continue reading",
    "read the rest",
    "read full",
    "weiterlesen",
)
_MIN_CONTENT_CHARS = 500


class FeedbinError(ClientError):
    """Raised when a Feedbin API call fails."""


def _chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _looks_truncated(html: str) -> bool:
    if not html or not html.strip():
        return True
    lowered = html.lower()
    if any(marker in lowered for marker in _TRUNCATION_MARKERS):
        return True
    text = BeautifulSoup(html, "lxml").get_text(strip=True)
    if len(text) < _MIN_CONTENT_CHARS:
        return True
    if text.rstrip().endswith(("…", "[…]", "[...]", "...")):
        return True
    return False


def _parse_published(raw):
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


class FeedbinClient:
    """Reads unread posts from Feedbin. Implements ``client.Client``."""

    def __init__(self, email, password, timeout=DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = (email, password)
        self.session.headers.update({"Content-Type": "application/json"})
        # Article id -> Feedbin's signed full-text extraction URL, from list_unread.
        self._extraction_urls: dict[str, str] = {}

    # --- Client interface ---

    def verify(self) -> None:
        """Check credentials via the authentication endpoint."""
        resp = self._request("GET", "authentication.json", check=False)
        if resp.status_code != 200:
            raise FeedbinError(
                f"Feedbin authentication failed (HTTP {resp.status_code}). "
                "Check your email and password in the config file."
            )

    def feed_titles(self) -> list[str]:
        titles = {title for title in self._subscriptions().values() if title}
        return sorted(titles, key=str.lower)

    def list_unread(self) -> list[Article]:
        """Every unread post, with the inline content Feedbin sends along."""
        entry_ids = self._unread_ids()
        entries = self._entries(entry_ids) if entry_ids else []
        feeds = self._subscriptions() if entries else {}

        articles = []
        self._extraction_urls = {}
        for entry in entries:
            article = Article(
                id=str(entry.get("id", "")),
                title=entry.get("title") or "(untitled)",
                html=entry.get("content") or "",
                feed_title=feeds.get(entry.get("feed_id", 0), ""),
                url=entry.get("url"),
                author=entry.get("author"),
                published=_parse_published(entry.get("published")),
            )
            extraction_url = entry.get("extracted_content_url")
            if extraction_url:
                self._extraction_urls[article.id] = extraction_url
            articles.append(article)
        return articles

    def resolve(
        self, articles: Sequence[Article], progress: Progress | None = None
    ) -> list[Article]:
        """Swap truncated inline content for Feedbin's full-text extraction.

        The inline content wins unless it's missing or looks like a teaser; the
        extraction is only fetched then, and only used when it has content.
        """
        resolved = []
        for done, article in enumerate(articles, 1):
            if _looks_truncated(article.html):
                extracted = self._extracted_content(
                    self._extraction_urls.get(article.id)
                )
                if extracted and extracted.strip():
                    article = replace(article, html=extracted)
            resolved.append(article)
            if progress:
                progress(done, len(articles), article.title)
        return resolved

    def mark_as_read(self, articles: Iterable[Article]) -> None:
        """Mark the given articles as read (in chunks of 1000)."""
        try:
            ids = [int(article.id) for article in articles]
        except ValueError as exc:
            raise FeedbinError(f"Not a Feedbin entry id: {exc}") from exc
        for chunk in _chunked(ids, UNREAD_CHUNK):
            self._request(
                "DELETE", "unread_entries.json", json={"unread_entries": list(chunk)}
            )

    # --- Feedbin specifics ---

    def _request(self, method, path, *, check=True, **kwargs):
        try:
            resp = self.session.request(
                method, f"{API_BASE}/{path}", timeout=self.timeout, **kwargs
            )
        except requests.RequestException as exc:
            raise FeedbinError(f"Could not reach Feedbin: {exc}") from exc
        if check and not resp.ok:
            raise FeedbinError(f"Feedbin returned HTTP {resp.status_code} for {path}.")
        return resp

    def _json(self, method, path, **kwargs):
        resp = self._request(method, path, **kwargs)
        try:
            return resp.json()
        except ValueError as exc:
            raise FeedbinError(f"Feedbin sent malformed JSON for {path}.") from exc

    def _unread_ids(self) -> list[int]:
        return self._json("GET", "unread_entries.json")

    def _entries(self, ids) -> list[dict]:
        """Fetch full entry objects for the given ids (in chunks of 100)."""
        entries: list[dict] = []
        for chunk in _chunked(list(ids), ENTRIES_CHUNK):
            params = {"ids": ",".join(str(i) for i in chunk)}
            entries.extend(self._json("GET", "entries.json", params=params))
        return entries

    def _subscriptions(self) -> dict[int, str]:
        """Return a mapping of feed_id -> feed title."""
        return {
            sub["feed_id"]: sub.get("title", "")
            for sub in self._json("GET", "subscriptions.json")
            if "feed_id" in sub
        }

    def _extracted_content(self, url) -> str | None:
        """Fetch Feedbin's full-content extraction for a pre-signed URL.

        The extracted_content_url is already HMAC-signed, so it needs no
        auth. Returns the extracted HTML content, or None on any failure.
        """
        if not url:
            return None
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json().get("content")
        except (requests.RequestException, ValueError):
            return None
