import base64

import requests
from requests.adapters import BaseAdapter

from feedpaper.feedbin import API_BASE, FeedbinClient

CREDENTIALS = "Basic " + base64.b64encode(b"me@example.com:hunter2").decode()


class RecordingAdapter(BaseAdapter):
    """Answers every request with an empty JSON list and keeps it for inspection."""

    def __init__(self):
        super().__init__()
        self.sent: list[requests.PreparedRequest] = []

    def send(self, request, *args, **kwargs):
        self.sent.append(request)
        response = requests.Response()
        response.status_code = 200
        response._content = b"[]"
        response.request = request
        response.url = request.url or ""
        return response

    def close(self):
        pass


def client_with_adapter():
    client = FeedbinClient("me@example.com", "hunter2")
    adapter = RecordingAdapter()
    client.session.mount("https://", adapter)
    client.session.mount("http://", adapter)
    return client, adapter


def test_api_requests_carry_the_credentials():
    client, adapter = client_with_adapter()

    client.verify()
    client.list_unread()

    assert [r.url for r in adapter.sent] == [
        f"{API_BASE}/authentication.json",
        f"{API_BASE}/unread_entries.json",
    ]
    assert all(r.headers["Authorization"] == CREDENTIALS for r in adapter.sent)


def test_the_session_itself_holds_no_credentials():
    client, adapter = client_with_adapter()

    client.session.get("https://images.example/a.png")
    client.session.get("http://images.example/a.png")

    assert client.session.auth is None
    assert all("Authorization" not in r.headers for r in adapter.sent)
