from __future__ import annotations

import html as html_module
import mimetypes
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from ebooklib import epub

STYLE = """
body { font-family: Georgia, serif; line-height: 1.5; margin: 5%; }
h1 { font-size: 1.5em; line-height: 1.2; margin: 0 0 0.2em; }
.byline { color: #555; font-size: 0.85em; margin-bottom: 1.5em; }
.byline a { color: #555; }
img { max-width: 100%; height: auto; }
pre { white-space: pre-wrap; word-wrap: break-word; }
blockquote { margin-left: 1em; padding-left: 1em; border-left: 3px solid #ccc; }
"""

# Tags removed entirely, including their content.
_STRIP_TAGS = ["script", "style", "iframe", "noscript", "object", "embed", "form"]

_IMAGE_TIMEOUT = 30


def _escape(text) -> str:
    return html_module.escape(text or "")


def sanitize_html(html: str) -> str:
    """Remove unsafe / noisy elements, keep readable markup and <img> tags."""
    soup = BeautifulSoup(html or "", "lxml")

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
        for src in (img.get("src", "") for img in soup.find_all("img"))
        if src and not src.startswith("data:")
    ]


def _byline(article) -> str:
    parts = [_escape(part) for part in (article.author, article.feed_title) if part]
    if article.published:
        parts.append(article.published.strftime("%Y-%m-%d"))
    meta = " · ".join(parts)
    source = f' · <a href="{_escape(article.url)}">Source</a>' if article.url else ""
    if not meta and not source:
        return ""
    return f'<p class="byline">{meta}{source}</p>'


def render_chapter(article, images) -> str:
    """Render one article as chapter XHTML.

    ``images`` maps an image URL to its path inside the book; an <img> whose
    source is missing from the map is dropped. Pure: no network, no disk.
    """
    soup = BeautifulSoup(sanitize_html(article.html), "lxml")
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or src.startswith("data:"):
            continue
        local = images.get(src)
        if local is None:
            img.decompose()
        else:
            img["src"] = local

    body = soup.body.decode_contents() if soup.body else str(soup)
    title = article.title or "(untitled)"
    return f"<h1>{_escape(title)}</h1>{_byline(article)}{body}"


def _guess_ext(url, media_type) -> str:
    if media_type:
        ext = mimetypes.guess_extension(media_type)
        if ext:
            return ".jpg" if ext == ".jpe" else ext
    suffix = Path(urlparse(url).path).suffix
    if suffix and len(suffix) <= 5:
        return suffix
    return ".jpg"


def http_fetch_image(url):
    """Download an image. Returns ``(data, media_type)``, or None on failure.

    Deliberately a bare request: the feed client's session carries the user's
    credentials, which have no business reaching arbitrary image hosts.
    """
    try:
        resp = requests.get(url, timeout=_IMAGE_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException:
        return None
    media_type = resp.headers.get("Content-Type", "").split(";")[0].strip()
    return resp.content, media_type


def _sort_key(article):
    # Newest first; articles without a date sort last.
    published = article.published
    return (1, published.timestamp()) if published else (0, 0.0)


def _collect_images(articles, fetch_image):
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


def render_epub(articles, out_dir, fetch_image=http_fetch_image, title=None) -> Path:
    """Render the given articles into an ePub and return the path written."""
    today = date.today()
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

    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", *chapters]

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"feedpaper-{today.isoformat()}.epub"
    epub.write_epub(str(out_path), book)
    return out_path
