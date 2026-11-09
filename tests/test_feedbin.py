import base64
import json

import pytest
import requests
from requests.adapters import BaseAdapter

from feedpaper.feedbin import API_BASE, FeedbinClient, FeedbinError

CREDENTIALS = "Basic " + base64.b64encode(b"me@example.com:hunter2").decode()
EXTRACTION_URL = "https://extract.feedbin.com/parser/feedbin/abc?base64_url=xyz"


class StubHttp(BaseAdapter):
    """A transport that answers from a URL -> (status, body) table and keeps
    every request it sends, so tests see the real, prepared requests."""

    def __init__(self, routes=None):
        super().__init__()
        self.routes = routes or {}
        self.sent: list[requests.PreparedRequest] = []

    def send(self, request, *args, **kwargs):
        self.sent.append(request)
        url = (request.url or "").split("?")[0]
        status, body = self.routes.get(url, (200, []))
        response = requests.Response()
        response.status_code = status
        response._content = body if isinstance(body, bytes) else json.dumps(body).encode()
        response.request = request
        response.url = request.url or ""
        return response

    def close(self):
        pass


def feedbin(routes=None):
    stub = StubHttp(routes)
    http = requests.Session()
    http.mount("https://", stub)
    http.mount("http://", stub)
    return FeedbinClient("me@example.com", "hunter2", http=http), stub


def test_api_requests_carry_the_credentials():
    client, stub = feedbin()

    client.verify()
    client.list_unread()

    assert [r.url for r in stub.sent] == [
        f"{API_BASE}/authentication.json",
        f"{API_BASE}/unread_entries.json",
    ]
    assert all(r.headers["Authorization"] == CREDENTIALS for r in stub.sent)


def test_the_http_session_never_holds_credentials():
    http = requests.Session()
    FeedbinClient("me@example.com", "hunter2", http=http)

    assert http.auth is None
    assert "Authorization" not in http.headers


def test_the_full_text_fetch_goes_without_credentials():
    long_teaser = "<p>Short. Read more</p>"
    client, stub = feedbin(
        {
            f"{API_BASE}/unread_entries.json": (200, [1]),
            f"{API_BASE}/entries.json": (
                200,
                [{"id": 1, "feed_id": 10, "content": long_teaser,
                  "extracted_content_url": EXTRACTION_URL}],
            ),
            f"{API_BASE}/subscriptions.json": (200, [{"feed_id": 10, "title": "A Blog"}]),
            EXTRACTION_URL.split("?")[0]: (200, {"content": "<p>The whole post</p>"}),
        }
    )

    (article,) = client.resolve(client.list_unread())

    assert article.html == "<p>The whole post</p>"
    (extraction,) = [r for r in stub.sent if not (r.url or "").startswith(API_BASE)]
    assert "Authorization" not in extraction.headers


@pytest.mark.parametrize("body", [[], ["not", "a", "dict"], {"content": None}, b"not json"])
def test_an_unusable_full_text_keeps_the_inline_content(body):
    client, _ = feedbin(
        {
            f"{API_BASE}/unread_entries.json": (200, [1]),
            f"{API_BASE}/entries.json": (
                200, [{"id": 1, "content": "<p>Teaser</p>", "extracted_content_url": EXTRACTION_URL}]
            ),
            EXTRACTION_URL.split("?")[0]: (200, body),
        }
    )

    (article,) = client.resolve(client.list_unread())

    assert article.html == "<p>Teaser</p>"


def test_a_server_error_becomes_a_feedbin_error():
    client, _ = feedbin({f"{API_BASE}/unread_entries.json": (500, {})})

    with pytest.raises(FeedbinError):
        client.list_unread()
