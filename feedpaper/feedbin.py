from __future__ import annotations

import requests

API_BASE = "https://api.feedbin.com/v2"
ENTRIES_CHUNK = 100  # max ids per /entries.json request
UNREAD_CHUNK = 1000  # max ids per mark-as-read request
DEFAULT_TIMEOUT = 30


class FeedbinError(Exception):
    """Raised when a Feedbin API call fails."""


def _chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i : i + size]


class FeedbinClient:
    def __init__(self, email, password, timeout=DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = (email, password)
        self.session.headers.update({"Content-Type": "application/json"})

    def verify(self) -> None:
        """Check credentials via the authentication endpoint."""
        resp = self.session.get(
            f"{API_BASE}/authentication.json", timeout=self.timeout
        )
        if resp.status_code != 200:
            raise FeedbinError(
                f"Feedbin authentication failed (HTTP {resp.status_code}). "
                "Check FEEDBIN_EMAIL / FEEDBIN_PASSWORD."
            )

    def get_unread_ids(self) -> list[int]:
        resp = self.session.get(
            f"{API_BASE}/unread_entries.json", timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def get_entries(self, ids) -> list[dict]:
        """Fetch full entry objects for the given ids (in chunks of 100)."""
        entries: list[dict] = []
        for chunk in _chunked(list(ids), ENTRIES_CHUNK):
            params = {"ids": ",".join(str(i) for i in chunk)}
            resp = self.session.get(
                f"{API_BASE}/entries.json", params=params, timeout=self.timeout
            )
            resp.raise_for_status()
            entries.extend(resp.json())
        return entries

    def get_feeds(self) -> dict[int, str]:
        """Return a mapping of feed_id -> feed title via subscriptions."""
        resp = self.session.get(
            f"{API_BASE}/subscriptions.json", timeout=self.timeout
        )
        resp.raise_for_status()
        return {
            sub["feed_id"]: sub.get("title", "")
            for sub in resp.json()
            if "feed_id" in sub
        }

    def get_extracted_content(self, url) -> str | None:
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

    def mark_as_read(self, ids) -> None:
        """Mark the given entry ids as read (in chunks of 1000)."""
        for chunk in _chunked(list(ids), UNREAD_CHUNK):
            resp = self.session.delete(
                f"{API_BASE}/unread_entries.json",
                json={"unread_entries": list(chunk)},
                timeout=self.timeout,
            )
            resp.raise_for_status()
