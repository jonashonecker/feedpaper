import base64
import json
from datetime import date, datetime, timedelta, timezone
from typing import Any

import pytest
import requests
from ebooklib import ITEM_DOCUMENT, ITEM_IMAGE, epub

from feedpaper import cli
from feedpaper.service import Article
from feedpaper.config import Config
from feedpaper.feedbin import API_BASE
from feedpaper.placeholder import VIDEO_PNG
from feedpaper.render import (
    VIDEO_PLACEHOLDER,
    http_fetch_image,
    image_urls,
    render_chapter,
    render_epub,
    sanitize_html,
    youtube_id,
)

from .conftest import PNG

TODAY = date(2026, 11, 9)


def article(**overrides: Any) -> Article:
    fields: dict[str, Any] = {"id": "1", "title": "A post", "html": "<p>Hello</p>", "feed_title": "A Blog"}
    fields.update(overrides)
    return Article(**fields)


def at(day: int, hour: int = 12, tz=timezone.utc) -> datetime:
    return datetime(2026, 11, day, hour, tzinfo=tz)


class FakeFetcher:
    """Stands in for the image download: serves PNGs, fails for ``/missing``."""

    def __init__(self, media_type="image/png"):
        self.media_type = media_type
        self.calls: list[str] = []

    def __call__(self, url):
        self.calls.append(url)
        if "missing" in url:
            return None
        return PNG, self.media_type


def build(tmp_path, articles, fetcher=None, **kwargs):
    path = render_epub(
        articles, tmp_path, fetch_image=fetcher or FakeFetcher(), today=TODAY, **kwargs
    )
    return path, epub.read_epub(str(path))


def chapters(book):
    return [
        item
        for item in book.get_items_of_type(ITEM_DOCUMENT)
        if item.file_name.startswith("chapter_")
    ]


def chapter_html(book, index=0):
    return chapters(book)[index].get_content().decode()


class TestSanitizeHtml:
    @pytest.mark.parametrize(
        "tag", ["script", "style", "iframe", "noscript", "object", "embed", "form"]
    )
    def test_removes_unsafe_tags_with_their_content(self, tag):
        cleaned = sanitize_html(f"<p>keep</p><{tag}>drop me</{tag}>")

        assert "keep" in cleaned
        assert "drop me" not in cleaned
        assert f"<{tag}" not in cleaned

    def test_removes_event_handlers_in_any_case(self):
        cleaned = sanitize_html('<p onclick="x()" ONMOUSEOVER="y()" class="c">t</p>')

        assert cleaned == '<p class="c">t</p>'

    def test_removes_javascript_urls(self):
        cleaned = sanitize_html(
            '<a href=" JavaScript:alert(1)">a</a><img src="javascript:x"/>'
        )

        assert "javascript" not in cleaned.lower()
        assert "<a>a</a>" in cleaned

    def test_keeps_readable_markup_links_and_images(self):
        html = (
            '<h2>Head</h2><p><a href="https://example.com">link</a></p>'
            '<blockquote>quote</blockquote><img src="https://example.com/a.png"/>'
        )

        assert sanitize_html(html) == html

    @pytest.mark.parametrize("html", ["", None])
    def test_handles_empty_content(self, html):
        assert sanitize_html(html) == ""


class TestImageUrls:
    def test_lists_remote_images_in_document_order(self):
        html = (
            '<img src="https://b.example/2.png"><p>text</p>'
            '<img src="https://a.example/1.png"><img src="https://b.example/2.png">'
        )

        assert image_urls(html) == [
            "https://b.example/2.png",
            "https://a.example/1.png",
            "https://b.example/2.png",
        ]

    def test_skips_data_uris_empty_sources_and_javascript(self):
        html = '<img src="data:image/png;base64,AAAA"><img src=""><img><img src="javascript:x">'

        assert image_urls(html) == []


class TestRenderChapter:
    def test_starts_with_the_escaped_title(self):
        html = render_chapter(article(title="Tom & <Jerry>"), {})

        assert html.startswith("<h1>Tom &amp; &lt;Jerry&gt;</h1>")

    def test_untitled_articles_get_a_placeholder(self):
        assert render_chapter(article(title=""), {}).startswith("<h1>(untitled)</h1>")

    def test_byline_has_author_blog_date_and_source(self):
        html = render_chapter(
            article(
                author="Ada <Lovelace>",
                feed_title="A Blog",
                published=at(9),
                url="https://example.com/post?a=1&b=2",
            ),
            {},
        )

        assert (
            '<p class="byline">Ada &lt;Lovelace&gt; · A Blog · 2026-11-09 · '
            '<a href="https://example.com/post?a=1&amp;b=2">Source</a></p>'
        ) in html

    def test_no_byline_without_any_metadata(self):
        html = render_chapter(article(feed_title="", author=None, url=None), {})

        assert "byline" not in html

    def test_points_images_at_their_copy_in_the_book(self):
        html = render_chapter(
            article(html='<img src="https://example.com/a.png">'),
            {"https://example.com/a.png": "images/img_1.png"},
        )

        assert '<img src="images/img_1.png"/>' in html

    def test_drops_images_that_were_not_downloaded(self):
        html = render_chapter(
            article(html='<p>text</p><img src="https://example.com/a.png">'), {}
        )

        assert "<img" not in html
        assert "<p>text</p>" in html

    def test_keeps_inline_data_images(self):
        html = render_chapter(article(html='<img src="data:image/png;base64,AAAA">'), {})

        assert 'src="data:image/png;base64,AAAA"' in html

    def test_sanitizes_the_content(self):
        html = render_chapter(article(html="<p>ok</p><script>alert(1)</script>"), {})

        assert "<script" not in html


class TestRenderEpub:
    def test_writes_a_readable_epub_named_after_the_day(self, tmp_path):
        path, book = build(tmp_path, [article()])

        assert path == tmp_path / "feedpaper-2026-11-09.epub"
        assert book.get_metadata("DC", "title")[0][0] == "feedpaper 2026-11-09"
        assert book.get_metadata("DC", "identifier")[0][0] == "feedpaper-2026-11-09"

    def test_uses_a_custom_title(self, tmp_path):
        _, book = build(tmp_path, [article()], title="Weekend reading")

        assert book.get_metadata("DC", "title")[0][0] == "Weekend reading"

    def test_creates_the_output_directory(self, tmp_path):
        path = render_epub(
            [article()], tmp_path / "a" / "b", fetch_image=FakeFetcher(), today=TODAY
        )

        assert path.exists()

    def test_orders_chapters_newest_first_and_undated_last(self, tmp_path):
        articles = [
            article(id="1", title="undated"),
            article(id="2", title="older", published=at(7)),
            article(id="3", title="newest", published=at(9)),
            article(id="4", title="middle", published=at(8)),
        ]

        _, book = build(tmp_path, articles)

        assert [chapter.title for chapter in book.toc] == [
            "newest",
            "middle",
            "older",
            "undated",
        ]

    def test_orders_by_the_actual_time_across_utc_offsets(self, tmp_path):
        # 10:00 in Berlin (UTC+1) is 09:00 UTC, so earlier than 09:30 UTC.
        berlin = timezone(timedelta(hours=1))
        articles = [
            article(id="1", title="berlin 10:00", published=at(9, 10, berlin)),
            article(id="2", title="utc 09:30", published=at(9, 9).replace(minute=30)),
        ]

        _, book = build(tmp_path, articles)

        assert [chapter.title for chapter in book.toc] == ["utc 09:30", "berlin 10:00"]

    def test_every_chapter_is_in_the_spine_and_table_of_contents(self, tmp_path):
        _, book = build(tmp_path, [article(id=str(i), title=f"t{i}") for i in range(3)])

        spine_ids = [item_id for item_id, _ in book.spine]
        assert len(book.toc) == 3
        assert all(chapter.id in spine_ids for chapter in chapters(book))

    def test_downloads_each_image_once_and_embeds_it(self, tmp_path):
        shared = "https://cdn.example/shared.png"
        fetcher = FakeFetcher()
        articles = [
            article(id="1", html=f'<img src="{shared}">'),
            article(id="2", html=f'<img src="{shared}"><img src="{shared}">'),
        ]

        _, book = build(tmp_path, articles, fetcher)

        assert fetcher.calls == [shared]
        images = list(book.get_items_of_type(ITEM_IMAGE))
        assert len(images) == 1
        assert images[0].get_content() == PNG
        for index in range(2):
            assert f'src="{images[0].file_name}"' in chapter_html(book, index)

    def test_drops_images_that_fail_to_download(self, tmp_path):
        articles = [
            article(
                html='<img src="https://cdn.example/missing.png"><img src="https://cdn.example/ok.png">'
            )
        ]

        _, book = build(tmp_path, articles)

        assert len(list(book.get_items_of_type(ITEM_IMAGE))) == 1
        assert "missing.png" not in chapter_html(book)

    @pytest.mark.parametrize(
        ("url", "media_type", "extension"),
        [
            ("https://cdn.example/photo.png", "image/jpeg", ".jpg"),
            ("https://cdn.example/photo", "image/gif", ".gif"),
            ("https://cdn.example/photo.webp?w=800", "", ".webp"),
            ("https://cdn.example/photo", "", ".jpg"),
        ],
    )
    def test_names_images_after_their_media_type_or_url(
        self, tmp_path, url, media_type, extension
    ):
        _, book = build(
            tmp_path, [article(html=f'<img src="{url}">')], FakeFetcher(media_type)
        )

        (image,) = book.get_items_of_type(ITEM_IMAGE)
        assert image.file_name.endswith(extension)


YOUTUBE_EMBED = '<iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe>'
YOUTUBE_THUMBNAIL = "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg"


class TestVideos:
    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ&t=42",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ?start=10",
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
            "//www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://www.youtube.com/live/dQw4w9WgXcQ",
        ],
    )
    def test_finds_the_youtube_id(self, url):
        assert youtube_id(url) == "dQw4w9WgXcQ"

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/",
            "https://www.youtube.com/watch?v=short",
            "https://www.youtube.com/embed/dQw4w9WgXcQ/extra",
            "https://www.youtube.com/@channel",
            "https://notyoutube.com/embed/dQw4w9WgXcQ",
            "https://vimeo.com/76979871",
        ],
    )
    def test_ignores_urls_without_a_youtube_video(self, url):
        assert youtube_id(url) is None

    def test_downloads_the_youtube_thumbnail(self, tmp_path):
        fetcher = FakeFetcher("image/jpeg")

        _, book = build(tmp_path, [article(html=YOUTUBE_EMBED)], fetcher)

        assert fetcher.calls == [YOUTUBE_THUMBNAIL]
        (image,) = book.get_items_of_type(ITEM_IMAGE)
        assert f'src="{image.file_name}"' in chapter_html(book)
        assert 'href="https://www.youtube.com/watch?v=dQw4w9WgXcQ"' in chapter_html(book)

    def test_falls_back_to_the_placeholder_when_the_thumbnail_fails(self, tmp_path):
        _, book = build(tmp_path, [article(html=YOUTUBE_EMBED)], lambda url: None)

        (image,) = book.get_items_of_type(ITEM_IMAGE)
        assert image.file_name == VIDEO_PLACEHOLDER
        assert image.get_content() == VIDEO_PNG
        assert f'src="{VIDEO_PLACEHOLDER}"' in chapter_html(book)

    def test_other_video_sites_get_the_placeholder_without_a_download(self, tmp_path):
        fetcher = FakeFetcher()
        html = '<iframe src="https://player.vimeo.com/video/76979871"></iframe>'

        _, book = build(tmp_path, [article(html=html)], fetcher)

        assert fetcher.calls == []
        assert [i.file_name for i in book.get_items_of_type(ITEM_IMAGE)] == [
            VIDEO_PLACEHOLDER
        ]
        assert 'href="https://vimeo.com/76979871"' in chapter_html(book)

    def test_adds_the_placeholder_once_for_several_videos(self, tmp_path):
        html = '<video src="https://media.example/a.mp4"></video>'

        _, book = build(
            tmp_path, [article(id="1", html=html), article(id="2", html=html)]
        )

        assert len(list(book.get_items_of_type(ITEM_IMAGE))) == 1

    def test_books_without_videos_have_no_placeholder(self, tmp_path):
        _, book = build(tmp_path, [article()])

        assert list(book.get_items_of_type(ITEM_IMAGE)) == []

    def test_other_iframes_are_still_dropped(self):
        assert sanitize_html('<iframe src="https://maps.example/embed"></iframe>') == ""


class TestHttpFetchImage:
    def test_returns_the_image_and_its_media_type(self, image_host):
        assert http_fetch_image(image_host.url("/a.png")) == (PNG, "image/png")

    def test_returns_none_for_an_http_error(self, image_host):
        assert http_fetch_image(image_host.url("/missing")) is None

    @pytest.mark.parametrize(
        "url", ["http://127.0.0.1:9/a.png", "/relative/a.png", "//cdn.example/a.png"]
    )
    def test_returns_none_when_the_url_cannot_be_fetched(self, url):
        assert http_fetch_image(url) is None


def test_image_hosts_never_see_the_feedbin_credentials(tmp_path, image_host, monkeypatch):
    """Regression test for GHSA-v7q9-7c6j-j6w8.

    Up to 0.1.3, images were downloaded through the authenticated Feedbin
    session, and every image host received the user's email and password.
    This runs the whole command with the real Feedbin adapter; only the Feedbin
    API itself is faked, and images come from a local server.
    """
    entries = [
        {"id": 1, "feed_id": 10, "title": "Pictures", "content": (
            f'<p>{"word " * 200}</p><img src="{image_host.url("/a.png")}">'
            f'<img src="{image_host.url("/missing")}">'
        )},
    ]
    api = {
        "authentication.json": {},
        "unread_entries.json": [1],
        "entries.json": entries,
        "subscriptions.json": [{"feed_id": 10, "title": "A Blog"}],
    }
    real_request = requests.Session.request

    def fake_feedbin(session, method, url, *args, **kwargs):
        if not url.startswith(API_BASE):
            return real_request(session, method, url, *args, **kwargs)
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps(api[url.removeprefix(f"{API_BASE}/")]).encode()
        return response

    monkeypatch.setattr(requests.Session, "request", fake_feedbin)
    monkeypatch.setattr(
        cli, "load_config", lambda: Config("me@example.com", "hunter2")
    )

    assert cli.main(["--output", str(tmp_path), "--keep-unread"]) == 0

    assert len(image_host.requests) == 2
    secret = base64.b64encode(b"me@example.com:hunter2").decode()
    for headers in image_host.requests:
        assert "authorization" not in headers
        assert secret not in "".join(headers.values())
