import base64
import json
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest
import requests
from requests.adapters import BaseAdapter

from feedpaper.feedbin import API_BASE, FeedbinAdapter, FeedbinError
from feedpaper.service import Article, FeedService, FeedServiceError

CREDENTIALS = "Basic " + base64.b64encode(b"me@example.com:hunter2").decode()
EXTRACTION_URL = "https://extract.feedbin.com/parser/feedbin/abc?base64_url=xyz"


class StubHttp(BaseAdapter):
    """A transport that answers from a URL -> (status, body) table and keeps
    every request it sends, so tests see the real, prepared requests.

    A table entry may also be a function of the request that returns
    (status, body) or raises, for answers that depend on the request.
    """

    def __init__(self, routes: dict[str, Any] | None = None):
        super().__init__()
        self.routes: dict[str, Any] = routes or {}
        self.sent: list[requests.PreparedRequest] = []

    def send(self, request, *args, **kwargs):
        self.sent.append(request)
        url = (request.url or "").split("?")[0]
        route: Any = self.routes.get(url, (200, []))
        answer: Any = route(request) if callable(route) else route
        status, body = answer
        response = requests.Response()
        response.status_code = status
        response._content = body if isinstance(body, bytes) else json.dumps(body).encode()
        response.request = request
        response.url = request.url or ""
        return response

    def close(self):
        pass


def requested_ids(request: requests.PreparedRequest) -> list[str]:
    """The entry ids an entries.json request asks for."""
    return parse_qs(urlparse(str(request.url)).query)["ids"][0].split(",")


def sent_json(request: requests.PreparedRequest) -> Any:
    """The JSON body of a request."""
    assert isinstance(request.body, (bytes, str))
    return json.loads(request.body)


def feedbin(routes: dict[str, Any] | None = None):
    stub = StubHttp(routes)
    http = requests.Session()
    http.mount("https://", stub)
    http.mount("http://", stub)
    return FeedbinAdapter("me@example.com", "hunter2", http=http), stub


def test_api_requests_carry_the_credentials():
    adapter, stub = feedbin()

    adapter.verify()
    adapter.list_unread()

    assert [r.url for r in stub.sent] == [
        f"{API_BASE}/authentication.json",
        f"{API_BASE}/unread_entries.json",
    ]
    assert all(r.headers["Authorization"] == CREDENTIALS for r in stub.sent)


def test_the_http_session_never_holds_credentials():
    http = requests.Session()
    FeedbinAdapter("me@example.com", "hunter2", http=http)

    assert http.auth is None
    assert "Authorization" not in http.headers


def test_the_full_text_fetch_goes_without_credentials():
    long_teaser = "<p>Short. Read more</p>"
    adapter, stub = feedbin(
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

    (article,) = adapter.resolve(adapter.list_unread())

    assert article.html == "<p>The whole post</p>"
    (extraction,) = [r for r in stub.sent if not (r.url or "").startswith(API_BASE)]
    assert "Authorization" not in extraction.headers


@pytest.mark.parametrize("body", [[], ["not", "a", "dict"], {"content": None}, b"not json"])
def test_an_unusable_full_text_keeps_the_inline_content(body):
    adapter, _ = feedbin(
        {
            f"{API_BASE}/unread_entries.json": (200, [1]),
            f"{API_BASE}/entries.json": (
                200, [{"id": 1, "content": "<p>Teaser</p>", "extracted_content_url": EXTRACTION_URL}]
            ),
            EXTRACTION_URL.split("?")[0]: (200, body),
        }
    )

    (article,) = adapter.resolve(adapter.list_unread())

    assert article.html == "<p>Teaser</p>"


def test_a_server_error_becomes_a_feedbin_error():
    adapter, _ = feedbin({f"{API_BASE}/unread_entries.json": (500, {})})

    with pytest.raises(FeedbinError):
        adapter.list_unread()


def test_the_adapter_is_a_feed_service():
    adapter, _ = feedbin()

    assert isinstance(adapter, FeedService)
    assert issubclass(FeedbinError, FeedServiceError)


class TestListUnread:
    def test_turns_feedbin_entries_into_articles(self):
        adapter, _ = feedbin(
            {
                f"{API_BASE}/unread_entries.json": (200, [7]),
                f"{API_BASE}/entries.json": (
                    200,
                    [
                        {
                            "id": 7,
                            "feed_id": 10,
                            "title": "A post",
                            "author": "Ada",
                            "content": "<p>Hello</p>",
                            "url": "https://blog.example/a-post",
                            "published": "2026-11-09T08:30:00.000000Z",
                        }
                    ],
                ),
                f"{API_BASE}/subscriptions.json": (
                    200,
                    [{"feed_id": 10, "title": "A Blog"}, {"feed_id": 11, "title": "Other"}],
                ),
            }
        )

        assert adapter.list_unread() == [
            Article(
                id="7",
                title="A post",
                html="<p>Hello</p>",
                feed_title="A Blog",
                url="https://blog.example/a-post",
                author="Ada",
                published=datetime(2026, 11, 9, 8, 30, tzinfo=timezone.utc),
            )
        ]

    def test_fills_in_what_an_entry_leaves_out(self):
        adapter, _ = feedbin(
            {
                f"{API_BASE}/unread_entries.json": (200, [7]),
                f"{API_BASE}/entries.json": (
                    200, [{"id": 7, "feed_id": 99, "title": None, "published": "soon"}]
                ),
            }
        )

        assert adapter.list_unread() == [
            Article(id="7", title="(untitled)", html="", feed_title="")
        ]

    def test_without_unread_posts_it_asks_for_nothing_else(self):
        adapter, stub = feedbin()

        assert adapter.list_unread() == []
        assert [r.url for r in stub.sent] == [f"{API_BASE}/unread_entries.json"]

    def test_fetches_entries_100_at_a_time(self):
        def entries(request):
            return 200, [{"id": int(i)} for i in requested_ids(request)]

        adapter, stub = feedbin(
            {
                f"{API_BASE}/unread_entries.json": (200, list(range(1, 151))),
                f"{API_BASE}/entries.json": entries,
            }
        )

        articles = adapter.list_unread()

        assert [a.id for a in articles] == [str(i) for i in range(1, 151)]
        requested = [
            len(requested_ids(r))
            for r in stub.sent
            if (r.url or "").startswith(f"{API_BASE}/entries.json")
        ]
        assert requested == [100, 50]


class TestResolve:
    ROUTES = {
        f"{API_BASE}/unread_entries.json": (200, [1, 2]),
        f"{API_BASE}/entries.json": (
            200,
            [
                {"id": 1, "title": "Full", "content": f"<p>{'word ' * 200}</p>",
                 "extracted_content_url": EXTRACTION_URL},
                {"id": 2, "title": "Teaser", "content": "<p>Read more</p>",
                 "extracted_content_url": EXTRACTION_URL},
            ],
        ),
        EXTRACTION_URL.split("?")[0]: (200, {"content": "<p>The whole post</p>"}),
    }

    def test_fetches_the_full_text_only_for_truncated_posts(self):
        adapter, stub = feedbin(self.ROUTES)

        full, teaser = adapter.resolve(adapter.list_unread())

        assert full.html.startswith("<p>word")
        assert teaser.html == "<p>The whole post</p>"
        assert len([r for r in stub.sent if (r.url or "").startswith("https://extract.")]) == 1

    def test_returns_the_same_posts_and_changes_only_their_content(self):
        adapter, _ = feedbin(self.ROUTES)
        listed = adapter.list_unread()

        resolved = adapter.resolve(listed)

        strip = lambda articles: [(a.id, a.title, a.feed_title, a.url) for a in articles]
        assert strip(resolved) == strip(listed)

    def test_reports_progress_for_every_post(self):
        adapter, _ = feedbin(self.ROUTES)
        seen = []

        adapter.resolve(adapter.list_unread(), progress=lambda *step: seen.append(step))

        assert seen == [(1, 2, "Full"), (2, 2, "Teaser")]


class TestMarkAsRead:
    def test_sends_exactly_the_given_ids(self):
        adapter, stub = feedbin()

        adapter.mark_as_read([Article("7", "t", "", ""), Article("9", "t", "", "")])

        (request,) = stub.sent
        assert (request.method, request.url) == ("DELETE", f"{API_BASE}/unread_entries.json")
        assert sent_json(request) == {"unread_entries": [7, 9]}
        assert request.headers["Content-Type"] == "application/json"

    def test_sends_1000_ids_at_a_time(self):
        adapter, stub = feedbin()

        adapter.mark_as_read(Article(str(i), "t", "", "") for i in range(1, 1002))

        sizes = [len(sent_json(r)["unread_entries"]) for r in stub.sent]
        assert sizes == [1000, 1]

    def test_sends_nothing_for_no_posts(self):
        adapter, stub = feedbin()

        adapter.mark_as_read([])

        assert stub.sent == []

    def test_rejects_an_id_feedbin_did_not_hand_out(self):
        adapter, stub = feedbin()

        with pytest.raises(FeedbinError, match="Not a Feedbin entry id"):
            adapter.mark_as_read([Article("tag:google.com,2005:reader/item/1", "t", "", "")])

        assert stub.sent == []


class TestFailures:
    def test_wrong_credentials_say_what_to_check(self):
        adapter, _ = feedbin({f"{API_BASE}/authentication.json": (401, {})})

        with pytest.raises(FeedbinError, match="HTTP 401.*email and password"):
            adapter.verify()

    def test_a_network_failure_becomes_a_feedbin_error(self):
        def offline(request):
            raise requests.ConnectionError("no route to host")

        adapter, _ = feedbin({f"{API_BASE}/unread_entries.json": offline})

        with pytest.raises(FeedbinError, match="Could not reach Feedbin"):
            adapter.list_unread()

    def test_malformed_json_becomes_a_feedbin_error(self):
        adapter, _ = feedbin({f"{API_BASE}/unread_entries.json": (200, b"<html>oops</html>")})

        with pytest.raises(FeedbinError, match="malformed JSON"):
            adapter.list_unread()

    def test_a_failed_mark_as_read_becomes_a_feedbin_error(self):
        adapter, _ = feedbin({f"{API_BASE}/unread_entries.json": (503, {})})

        with pytest.raises(FeedbinError, match="HTTP 503"):
            adapter.mark_as_read([Article("7", "t", "", "")])
