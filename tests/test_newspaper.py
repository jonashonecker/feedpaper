from datetime import date

import pytest
from ebooklib import epub

from feedpaper.newspaper import Newspaper, Reporter, build_newspaper
from feedpaper.service import Article, FeedService, FeedServiceError

from .fakes import FakeService, fake_fetch_image
from .test_render import chapter_html

TODAY = date(2026, 11, 11)


def post(id: str, title: str, feed_title: str = "Good Blog") -> Article:
    return Article(id=id, title=title, html=f"<p>{title}</p>", feed_title=feed_title)


POSTS = [post("1", "First"), post("2", "Second"), post("3", "Skipped", "Bad Blog")]


def build(service, tmp_path, **kwargs) -> Newspaper:
    return build_newspaper(
        service, tmp_path, fetch_image=fake_fetch_image, today=TODAY, **kwargs
    )


def chapter_titles(newspaper: Newspaper) -> list[str]:
    assert newspaper.path is not None
    return sorted(chapter.title for chapter in epub.read_epub(str(newspaper.path)).toc)


class RecordingReporter(Reporter):
    def __init__(self):
        self.events: list[tuple] = []

    def found(self, count):
        self.events.append(("found", count))

    def excluded(self, count, feed_titles):
        self.events.append(("excluded", count, feed_titles))

    def resolving(self, count):
        self.events.append(("resolving", count))

    def resolved(self, done, total, title):
        self.events.append(("resolved", done, total, title))

    def rendering(self):
        self.events.append(("rendering",))


def test_the_fake_service_is_a_feed_service():
    assert isinstance(FakeService(), FeedService)


def test_builds_an_epub_from_the_unread_posts_and_marks_them_as_read(tmp_path):
    service = FakeService(POSTS)

    newspaper = build(service, tmp_path)

    assert newspaper.path == tmp_path / "feedpaper-2026-11-11.epub"
    assert chapter_titles(newspaper) == ["First", "Second", "Skipped"]
    assert (newspaper.found, newspaper.excluded) == (3, 0)
    assert newspaper.marked_read and newspaper.mark_error is None
    assert service.marked == ["1", "2", "3"]
    assert service.unread == []


class TestExcludedBlogs:
    def test_their_posts_stay_out_of_the_newspaper(self, tmp_path):
        newspaper = build(FakeService(POSTS), tmp_path, excluded_blogs=["Bad Blog"])

        assert chapter_titles(newspaper) == ["First", "Second"]
        assert (newspaper.found, newspaper.excluded) == (3, 1)
        assert [a.id for a in newspaper.articles] == ["1", "2"]

    def test_their_posts_stay_unread(self, tmp_path):
        service = FakeService(POSTS)

        build(service, tmp_path, excluded_blogs=["Bad Blog"])

        assert service.marked == ["1", "2"]
        assert [a.id for a in service.unread] == ["3"]

    def test_their_posts_cost_no_full_content_fetch(self, tmp_path):
        service = FakeService(POSTS)

        build(service, tmp_path, excluded_blogs=["Bad Blog"])

        assert service.resolved == ["1", "2"]

    def test_blog_titles_match_whatever_their_case_or_padding(self, tmp_path):
        newspaper = build(FakeService(POSTS), tmp_path, excluded_blogs=["  bad BLOG "])

        assert newspaper.excluded == 1

    def test_when_every_post_is_excluded_nothing_happens(self, tmp_path):
        service = FakeService(POSTS)

        newspaper = build(service, tmp_path, excluded_blogs=["Good Blog", "Bad Blog"])

        assert newspaper == Newspaper(found=3, excluded=3)
        assert list(tmp_path.iterdir()) == []
        assert service.resolved == [] and service.marked == []


def test_keep_unread_builds_the_epub_and_marks_nothing(tmp_path):
    service = FakeService(POSTS)

    newspaper = build(service, tmp_path, keep_unread=True)

    assert newspaper.path is not None and newspaper.path.exists()
    assert not newspaper.marked_read and newspaper.mark_error is None
    assert service.marked == []
    assert len(service.unread) == 3


def test_without_unread_posts_nothing_happens(tmp_path):
    service = FakeService()

    newspaper = build(service, tmp_path)

    assert newspaper == Newspaper(found=0, excluded=0)
    assert list(tmp_path.iterdir()) == []


def test_the_newspaper_holds_the_resolved_content(tmp_path):
    service = FakeService([post("1", "Teaser")], full_text={"1": "<p>The whole story</p>"})

    newspaper = build(service, tmp_path)

    assert newspaper.articles[0].html == "<p>The whole story</p>"
    assert "The whole story" in chapter_html(epub.read_epub(str(newspaper.path)))


def test_only_posts_in_the_newspaper_are_marked_as_read(tmp_path):
    """What resolve returns is what gets marked: nothing more, nothing less."""
    service = FakeService(POSTS)

    newspaper = build(service, tmp_path, excluded_blogs=["Bad Blog"])

    assert service.marked == [a.id for a in newspaper.articles]


def test_a_failure_to_mark_as_read_keeps_the_epub(tmp_path):
    service = FakeService(POSTS)
    service.fail_mark = True

    newspaper = build(service, tmp_path)

    assert newspaper.path is not None and newspaper.path.exists()
    assert not newspaper.marked_read
    assert str(newspaper.mark_error) == "service is down"


def test_a_failure_to_list_posts_raises_and_writes_nothing(tmp_path):
    service = FakeService(POSTS)
    service.fail_list = True

    with pytest.raises(FeedServiceError):
        build(service, tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_reports_each_step_in_order(tmp_path):
    reporter = RecordingReporter()

    build(FakeService(POSTS), tmp_path, excluded_blogs=["Bad Blog"], reporter=reporter)

    assert reporter.events == [
        ("found", 3),
        ("excluded", 1, ["Bad Blog"]),
        ("resolving", 2),
        ("resolved", 1, 2, "First"),
        ("resolved", 2, 2, "Second"),
        ("rendering",),
    ]


def test_reports_only_the_count_when_nothing_is_unread(tmp_path):
    reporter = RecordingReporter()

    build(FakeService(), tmp_path, reporter=reporter)

    assert reporter.events == [("found", 0)]
