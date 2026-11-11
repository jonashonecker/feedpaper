import pytest

from feedpaper import cli
from feedpaper.config import Config
from feedpaper.service import Article

from .fakes import FakeService


def post(id: str, title: str, feed_title: str) -> Article:
    return Article(id=id, title=title, html=f"<p>{title}</p>", feed_title=feed_title)


POSTS = [
    post("1", "First", "Good Blog"),
    post("2", "Second", "Good Blog"),
    post("3", "Skipped", "Bad Blog"),
]


@pytest.fixture
def run(monkeypatch, tmp_path, capsys):
    """Run the command against a fake service; returns (exit code, stdout, stderr)."""

    def run(service, *args, excluded=()):
        config = Config("me@example.com", "hunter2", tuple(excluded))
        monkeypatch.setattr(cli, "load_config", lambda: config)
        monkeypatch.setattr(cli, "FeedbinAdapter", lambda email, password: service)
        code = cli.main(["--output", str(tmp_path), *args])
        out, err = capsys.readouterr()
        return code, out.replace(str(tmp_path), "OUT"), err

    return run


def epub_name(tmp_path):
    (path,) = tmp_path.glob("*.epub")
    return path.name


def test_builds_the_newspaper_and_marks_posts_as_read(run, tmp_path):
    service = FakeService(POSTS)

    code, out, err = run(service, excluded=["bad blog"])

    assert code == 0
    assert err == ""
    assert out.splitlines() == [
        "Authenticated with Feedbin.",
        "Found 3 unread post(s).",
        "Excluding 1 post(s) from: Bad Blog (kept unread).",
        "Resolving content...",
        "  [1/2] First",
        "  [2/2] Second",
        "Building ePub...",
        f"Wrote OUT/{epub_name(tmp_path)}",
        "Marked 2 post(s) as read on Feedbin.",
    ]
    assert service.marked == ["1", "2"]


def test_keep_unread_marks_nothing(run):
    service = FakeService(POSTS)

    code, out, _ = run(service, "--keep-unread")

    assert code == 0
    assert out.splitlines()[-1] == (
        "Skipped marking as read (--keep-unread). 3 post(s) stay unread."
    )
    assert service.marked == []


def test_without_unread_posts_there_is_nothing_to_do(run, tmp_path):
    code, out, _ = run(FakeService())

    assert code == 0
    assert out.splitlines() == [
        "Authenticated with Feedbin.",
        "No unread posts. Nothing to do.",
    ]
    assert list(tmp_path.iterdir()) == []


def test_when_every_post_is_excluded_nothing_is_built(run, tmp_path):
    service = FakeService(POSTS)

    code, out, _ = run(service, excluded=["Good Blog", "Bad Blog"])

    assert code == 0
    assert out.splitlines() == [
        "Authenticated with Feedbin.",
        "Found 3 unread post(s).",
        "Excluding 3 post(s) from: Bad Blog, Good Blog (kept unread).",
        "All unread posts are from excluded feeds. Nothing to build.",
    ]
    assert list(tmp_path.iterdir()) == []
    assert service.marked == []


def test_a_failure_to_mark_as_read_keeps_the_epub_and_exits_1(run, tmp_path):
    service = FakeService(POSTS)
    service.fail_mark = True

    code, out, err = run(service)

    assert code == 1
    assert out.splitlines()[-1] == f"Wrote OUT/{epub_name(tmp_path)}"
    assert err == "warning: ePub built but failed to mark as read: service is down\n"


def test_wrong_credentials_exit_1(run, tmp_path):
    service = FakeService(POSTS)
    service.fail_verify = True

    code, out, err = run(service)

    assert (code, out, err) == (1, "", "error: wrong password\n")
    assert list(tmp_path.iterdir()) == []


def test_a_service_failure_exits_1_without_an_epub(run, tmp_path):
    service = FakeService(POSTS)
    service.fail_list = True

    code, _, err = run(service)

    assert (code, err) == (1, "error: service is down\n")
    assert list(tmp_path.iterdir()) == []


def test_list_feeds_prints_the_blog_titles(run, tmp_path):
    code, out, _ = run(FakeService(POSTS), "--list-feeds")

    assert code == 0
    assert out.splitlines() == ["Authenticated with Feedbin.", "Bad Blog", "Good Blog"]
    assert list(tmp_path.iterdir()) == []
