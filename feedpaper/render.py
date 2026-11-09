from __future__ import annotations

import html as html_module
import mimetypes
from collections.abc import Callable, Iterable, Sequence
from datetime import date
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from ebooklib import epub

from feedpaper.client import Article
from feedpaper.placeholder import VIDEO_PNG

# Downloads one image: (data, media type), or None when it can't be fetched.
ImageFetcher = Callable[[str], tuple[bytes, str] | None]

STYLE = """
body { font-family: Georgia, serif; line-height: 1.5; margin: 5%; }
h1 { font-size: 1.5em; line-height: 1.2; margin: 0 0 0.2em; }
.byline { color: #555; font-size: 0.85em; margin-bottom: 1.5em; }
.byline a { color: #555; }
img { max-width: 100%; height: auto; }
pre { white-space: pre-wrap; word-wrap: break-word; }
blockquote { margin-left: 1em; padding-left: 1em; border-left: 3px solid #ccc; }
figure { margin: 1em 0; }
figcaption { color: #555; font-size: 0.85em; }
"""

# Tags removed entirely, including their content.
_STRIP_TAGS = ["script", "style", "iframe", "noscript", "object", "embed", "form"]

_IMAGE_TIMEOUT = 30

# Videos can't play in an ePub, so each one becomes a figure: a thumbnail that
# links to the video, and a caption with the same link. YouTube videos get their
# real thumbnail; every other video gets the placeholder image, which also
# stands in when a thumbnail fails to download.
VIDEO_PLACEHOLDER = "images/video.png"
_PLACEHOLDER_SRC = "feedpaper:video"  # never downloaded; render_chapter swaps it
_THUMBNAIL_CLASS = "video-thumbnail"

_YOUTUBE_HOSTS = {
    "youtube.com",
    "m.youtube.com",
    "youtube-nocookie.com",
    "youtu.be",
}
_YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
# Embedded players from other video sites; any other <iframe> is dropped.
_VIDEO_HOSTS = _YOUTUBE_HOSTS | {
    "player.vimeo.com",
    "vimeo.com",
    "dailymotion.com",
    "player.twitch.tv",
    "fast.wistia.net",
    "loom.com",
    "streamable.com",
}


def _escape(text: str | None) -> str:
    return html_module.escape(text or "")


def _src(img: Tag) -> str:
    """An <img>'s ``src`` as a string; empty when it's missing."""
    value = img.get("src")
    return value if isinstance(value, str) else ""


def _host(url: str) -> str:
    host = urlparse(url).hostname or ""
    return host.removeprefix("www.")


def _absolute(url: str) -> str | None:
    """``url`` as an absolute http(s) URL, or None if it isn't one."""
    if url.startswith("//"):
        url = f"https:{url}"
    return url if urlparse(url).scheme in ("http", "https") else None


def youtube_id(url: str) -> str | None:
    """The video id in a YouTube watch, short, embed or youtu.be URL."""
    parsed = urlparse(_absolute(url) or "")
    host = (parsed.hostname or "").removeprefix("www.")
    if host not in _YOUTUBE_HOSTS:
        return None
    if host == "youtu.be":
        candidate = parsed.path.strip("/")
    elif parsed.path == "/watch":
        candidate = parse_qs(parsed.query).get("v", [""])[0]
    else:
        parts = parsed.path.strip("/").split("/")
        candidate = parts[1] if len(parts) == 2 and parts[0] in ("embed", "shorts", "live", "v") else ""
    return candidate if _YOUTUBE_ID.match(candidate) else None


def _video_figure(soup: BeautifulSoup, url: str | None, thumbnail: str | None) -> Tag:
    link = _absolute(url) if url else None
    video_id = youtube_id(link) if link else None
    if video_id:
        link = f"https://www.youtube.com/watch?v={video_id}"
        thumbnail = thumbnail or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    if link and _host(link) == "player.vimeo.com":
        link = f"https://vimeo.com/{urlparse(link).path.rstrip('/').rsplit('/', 1)[-1]}"

    figure = soup.new_tag("figure", attrs={"class": "video"})
    image = soup.new_tag(
        "img",
        attrs={
            "class": _THUMBNAIL_CLASS,
            "src": _absolute(thumbnail or "") or _PLACEHOLDER_SRC,
            "alt": "Video",
        },
    )
    caption = soup.new_tag("figcaption")
    if link:
        image_link = soup.new_tag("a", href=link)
        image_link.append(image)
        figure.append(image_link)
        caption_link = soup.new_tag("a", href=link)
        caption_link.string = f"▶ Watch the video on {_host(link)}"
        caption.append(caption_link)
    else:
        figure.append(image)
        caption.string = "▶ A video that can't be shown here"
    figure.append(caption)
    return figure


def _replace_videos(soup: BeautifulSoup) -> None:
    """Swap embedded players and <video> elements for a linked thumbnail."""
    for iframe in soup.find_all("iframe"):
        src = _absolute(_src(iframe))
        if src and _host(src) in _VIDEO_HOSTS:
            iframe.replace_with(_video_figure(soup, src, None))
    for video in soup.find_all("video"):
        url = _src(video)
        if not url:
            source = video.find("source")
            url = _src(source) if isinstance(source, Tag) else ""
        poster = video.get("poster")
        video.replace_with(
            _video_figure(soup, url or None, poster if isinstance(poster, str) else None)
        )


def sanitize_html(html: str) -> str:
    """Remove unsafe / noisy elements, keep readable markup and <img> tags.

    Videos become a linked thumbnail first, since an ePub can't play them.
    """
    soup = BeautifulSoup(html or "", "lxml")
    _replace_videos(soup)

    for tag in soup(_STRIP_TAGS):
        tag.decompose()

    for tag in soup.find_all(True):
        # Drop inline event handlers (onclick, onload, ...).
        for attr in list(tag.attrs):
            if attr.lower().startswith("on"):
                del tag.attrs[attr]
        # Drop javascript: URLs.
        for url_attr in ("href", "src"):
            value = tag.get(url_attr)
            if isinstance(value, str) and value.strip().lower().startswith("javascript:"):
                del tag.attrs[url_attr]

    # lxml wraps fragments in <html><body>; return the inner body content.
    body = soup.body
    if body is not None:
        return body.decode_contents()
    return str(soup)


def image_urls(html: str) -> list[str]:
    """Every remote <img> source in the article, in document order."""
    soup = BeautifulSoup(sanitize_html(html), "lxml")
    return [
        src
        for src in (_src(img) for img in soup.find_all("img"))
        if src and not src.startswith("data:") and src != _PLACEHOLDER_SRC
    ]


def _byline(article: Article) -> str:
    parts = [_escape(part) for part in (article.author, article.feed_title) if part]
    if article.published:
        parts.append(article.published.strftime("%Y-%m-%d"))
    meta = " · ".join(parts)
    source = f' · <a href="{_escape(article.url)}">Source</a>' if article.url else ""
    if not meta and not source:
        return ""
    return f'<p class="byline">{meta}{source}</p>'


def render_chapter(article: Article, images: dict[str, str]) -> str:
    """Render one article as chapter XHTML.

    ``images`` maps an image URL to its path inside the book; an <img> whose
    source is missing from the map is dropped. Pure: no network, no disk.
    """
    soup = BeautifulSoup(sanitize_html(article.html), "lxml")
    for img in soup.find_all("img"):
        src = _src(img)
        if not src or src.startswith("data:"):
            continue
        local = images.get(src)
        if local is None and _THUMBNAIL_CLASS in img.get_attribute_list("class"):
            local = VIDEO_PLACEHOLDER
        if local is None:
            img.decompose()
        else:
            img["src"] = local

    body = soup.body.decode_contents() if soup.body else str(soup)
    title = article.title or "(untitled)"
    return f"<h1>{_escape(title)}</h1>{_byline(article)}{body}"


def _guess_ext(url: str, media_type: str) -> str:
    if media_type:
        ext = mimetypes.guess_extension(media_type)
        if ext:
            return ".jpg" if ext == ".jpe" else ext
    suffix = Path(urlparse(url).path).suffix
    if suffix and len(suffix) <= 5:
        return suffix
    return ".jpg"


def http_fetch_image(url: str) -> tuple[bytes, str] | None:
    """Download an image. Returns ``(data, media_type)``, or None on failure.

    Deliberately a bare request, apart from any feed service's HTTP session, so
    nothing meant for the service can reach arbitrary image hosts.
    """
    try:
        resp = requests.get(url, timeout=_IMAGE_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException:
        return None
    media_type = resp.headers.get("Content-Type", "").split(";")[0].strip()
    return resp.content, media_type


def _sort_key(article: Article) -> tuple[int, float]:
    # Newest first; articles without a date sort last.
    published = article.published
    return (1, published.timestamp()) if published else (0, 0.0)


def _collect_images(
    articles: Iterable[Article], fetch_image: ImageFetcher
) -> tuple[dict[str, str], list[epub.EpubImage]]:
    """Download each distinct image once; return {url: path} and the book items."""
    urls = dict.fromkeys(url for article in articles for url in image_urls(article.html))

    images: dict[str, str] = {}
    items = []
    for number, url in enumerate(urls, 1):
        fetched = fetch_image(url)
        if not fetched:
            continue
        data, media_type = fetched
        filename = f"images/img_{number}{_guess_ext(url, media_type)}"
        items.append(
            epub.EpubImage(
                uid=f"img_{number}",
                file_name=filename,
                media_type=media_type or "image/jpeg",
                content=data,
            )
        )
        images[url] = filename
    return images, items


def render_epub(
    articles: Sequence[Article],
    out_dir: str | Path,
    fetch_image: ImageFetcher = http_fetch_image,
    title: str | None = None,
    today: date | None = None,
) -> Path:
    """Render the given articles into an ePub and return the path written.

    ``today`` dates the title, the book's identifier and the file name; it
    defaults to the current date.
    """
    today = today or date.today()
    title = title or f"feedpaper {today.isoformat()}"

    book = epub.EpubBook()
    book.set_identifier(f"feedpaper-{today.isoformat()}")
    book.set_title(title)
    book.set_language("en")
    book.add_author("feedpaper")

    style_item = epub.EpubItem(
        uid="style",
        file_name="style/main.css",
        media_type="text/css",
        content=STYLE,
    )
    book.add_item(style_item)

    ordered = sorted(articles, key=_sort_key, reverse=True)
    images, image_items = _collect_images(ordered, fetch_image)
    for item in image_items:
        book.add_item(item)

    chapters = []
    for index, article in enumerate(ordered):
        chapter = epub.EpubHtml(
            title=article.title or "(untitled)",
            file_name=f"chapter_{index:04d}.xhtml",
            lang="en",
        )
        chapter.content = render_chapter(article, images)
        chapter.add_link(href=style_item.file_name, rel="stylesheet", type="text/css")
        book.add_item(chapter)
        chapters.append(chapter)

    if any(f'src="{VIDEO_PLACEHOLDER}"' in chapter.content for chapter in chapters):
        book.add_item(
            epub.EpubImage(
                uid="video_placeholder",
                file_name=VIDEO_PLACEHOLDER,
                media_type="image/png",
                content=VIDEO_PNG,
            )
        )

    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", *chapters]

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"feedpaper-{today.isoformat()}.epub"
    epub.write_epub(str(out_path), book)
    return out_path
