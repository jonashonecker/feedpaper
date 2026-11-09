import http.server
import threading
from dataclasses import dataclass, field

import pytest

# A 1x1 transparent PNG.
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082"
)


@dataclass
class ImageHost:
    """A local HTTP server standing in for a third-party image host."""

    base_url: str
    requests: list[dict[str, str]] = field(default_factory=list)

    def url(self, path: str) -> str:
        return f"{self.base_url}{path}"


@pytest.fixture
def image_host(monkeypatch):
    """Serve ``/*.png`` as an image and 404 for everything else.

    Every request's headers are recorded, so tests can check what a request
    carried, such as an ``Authorization`` header.
    """
    # The server is local; keep any configured proxy out of the way.
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")

    recorded: list[dict[str, str]] = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            recorded.append({k.lower(): v for k, v in self.headers.items()})
            if self.path.endswith(".png"):
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                self.wfile.write(PNG)
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield ImageHost(f"http://127.0.0.1:{server.server_port}", recorded)
    finally:
        server.shutdown()
        server.server_close()


def pytest_addoption(parser):
    parser.addoption(
        "--update-snapshots",
        action="store_true",
        help="Rewrite the expected output of the snapshot tests instead of comparing.",
    )


@pytest.fixture
def update_snapshots(request) -> bool:
    return bool(request.config.getoption("--update-snapshots"))
