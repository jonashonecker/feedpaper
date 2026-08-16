from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

DEFAULT_TIMEOUT = 30
ITEMS_CHUNK = 50  # FreshRSS's Fever endpoint caps items per request at 50, even with `with_ids`

# Stripped before hunting for the article body, so they can't win the "biggest
# text block" heuristic below.
_NON_CONTENT_TAGS = ["script", "style", "nav", "header", "footer", "aside", "noscript", "form", "iframe"]
_MIN_ARTICLE_CHARS = 200  # below this, treat extraction as having failed


class FreshRSSError(Exception):
    """Raised when a FreshRSS API call fails."""


def _chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _extract_article_html(page_html: str) -> str | None:
    """Pull the likely article body out of a full webpage's HTML.

    FreshRSS's Fever API has no full-text-extraction endpoint (unlike Feedbin's
    `extracted_content_url`), so when `fetch_full_content` is enabled feedpaper
    scrapes the linked page itself. This is a simple heuristic, not a real
    readability algorithm: prefer an `<article>` / `<main>` / role="main"
    element, and otherwise fall back to the div/section with the most text.
    """
    soup = BeautifulSoup(page_html or "", "lxml")
    for tag in soup(_NON_CONTENT_TAGS):
        tag.decompose()

    candidate = soup.find("article") or soup.find("main") or soup.find(attrs={"role": "main"})
    if candidate is None:
        containers = soup.find_all(["div", "section"])
        candidate = max(containers, key=lambda t: len(t.get_text(strip=True)), default=None)

    if candidate is None or len(candidate.get_text(strip=True)) < _MIN_ARTICLE_CHARS:
        return None
    return candidate.decode_contents()


def _normalize_entry(item: dict) -> dict:
    """Map a Fever `item` object onto feedpaper's canonical entry shape."""
    created = item.get("created_on_time")
    published = (
        datetime.fromtimestamp(created, tz=timezone.utc).isoformat()
        if created
        else None
    )
    return {
        "id": item.get("id"),
        "feed_id": item.get("feed_id"),
        "title": item.get("title"),
        "author": item.get("author"),
        "content": item.get("html") or "",
        "url": item.get("url"),
        "published": published,
        # The Fever API has no separate full-text-extraction endpoint like
        # Feedbin's; whatever FreshRSS scraping rules produced is already in `html`.
        "extracted_content_url": None,
    }


class FreshRSSClient:
    def __init__(self, url, user, password, timeout=DEFAULT_TIMEOUT):
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        api_key = hashlib.md5(f"{user}:{password}".encode("utf-8")).hexdigest()
        self._auth = {"api_key": api_key}

    def _request(self, flags, data=None) -> dict:
        """POST to the Fever endpoint with `flags` (e.g. ["api", "items"]) as the
        query string and `data` (merged with the api_key) as the POST body.
        """
        query = "&".join(flags)
        resp = self.session.post(
            f"{self.url}?{query}",
            data={**self._auth, **(data or {})},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        body = resp.json()
        if not body.get("auth"):
            raise FreshRSSError(
                "FreshRSS authentication failed. Check your URL, username, and "
                "API password in the config file."
            )
        return body

    def verify(self) -> None:
        """Check credentials via an unadorned API call."""
        self._request(["api"])

    def get_unread_ids(self) -> list[int]:
        body = self._request(["api", "unread_item_ids"])
        raw = body.get("unread_item_ids") or ""
        return [int(i) for i in raw.split(",") if i]

    def get_entries(self, ids) -> list[dict]:
        """Fetch full entry objects for the given ids (in chunks of 50)."""
        entries: list[dict] = []
        for chunk in _chunked(list(ids), ITEMS_CHUNK):
            body = self._request(
                ["api", "items"],
                data={"with_ids": ",".join(str(i) for i in chunk)},
            )
            entries.extend(_normalize_entry(item) for item in body.get("items", []))
        return entries

    def get_feeds(self) -> dict[int, str]:
        """Return a mapping of feed_id -> feed title."""
        body = self._request(["api", "feeds"])
        return {feed["id"]: feed.get("title", "") for feed in body.get("feeds", [])}

    def get_extracted_content(self, url) -> str | None:
        """FreshRSS's Fever API has no full-content extraction endpoint."""
        return None

    def fetch_full_content(self, url) -> str | None:
        """Fetch the article page behind `url` and extract its main content.

        Only used when `fetch_full_content` is enabled in the config. Returns
        None on any request failure or if no substantial article body is found.
        """
        if not url:
            return None
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
        except requests.RequestException:
            return None
        return _extract_article_html(resp.text)

    def mark_as_read(self, ids) -> None:
        """Mark the given entry ids as read (in chunks of 50)."""
        for chunk in _chunked(list(ids), ITEMS_CHUNK):
            self._request(
                ["api"],
                data={
                    "mark": "item",
                    "as": "read",
                    "with_ids": ",".join(str(i) for i in chunk),
                },
            )
