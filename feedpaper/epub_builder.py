from __future__ import annotations

import html as html_module
import mimetypes
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from ebooklib import epub

from feedpaper.content import sanitize_html

STYLE = """
body { font-family: Georgia, serif; line-height: 1.5; margin: 5%; }
h1 { font-size: 1.5em; line-height: 1.2; margin: 0 0 0.2em; }
.byline { color: #555; font-size: 0.85em; margin-bottom: 1.5em; }
.byline a { color: #555; }
img { max-width: 100%; height: auto; }
pre { white-space: pre-wrap; word-wrap: break-word; }
blockquote { margin-left: 1em; padding-left: 1em; border-left: 3px solid #ccc; }
"""

_IMAGE_TIMEOUT = 30


def _escape(text) -> str:
    return html_module.escape(text or "")


def _parse_published(entry):
    raw = entry.get("published")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _byline(entry, feed_title) -> str:
    parts = []
    if entry.get("author"):
        parts.append(_escape(entry["author"]))
    if feed_title:
        parts.append(_escape(feed_title))
    dt = _parse_published(entry)
    if dt:
        parts.append(dt.strftime("%Y-%m-%d"))
    meta = " · ".join(parts)
    url = entry.get("url")
    source = f' · <a href="{_escape(url)}">Source</a>' if url else ""
    if not meta and not source:
        return ""
    return f'<p class="byline">{meta}{source}</p>'


def _guess_ext(url, content_type) -> str:
    if content_type:
        ext = mimetypes.guess_extension(content_type)
        if ext:
            return ".jpg" if ext == ".jpe" else ext
    suffix = Path(urlparse(url).path).suffix
    if suffix and len(suffix) <= 5:
        return suffix
    return ".jpg"


def _download_image(session, url):
    try:
        resp = session.get(url, timeout=_IMAGE_TIMEOUT)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "").split(";")[0].strip()
        return resp.content, content_type
    except requests.RequestException:
        return None, None


def _embed_images(book, soup, session, state):
    """Download <img> sources, add them to the book, rewrite src to local path.

    ``state`` carries {"urls": {src: filename}, "counter": int} across chapters
    so identical images are only stored once.
    """
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or src.startswith("data:"):
            continue
        if src not in state["urls"]:
            data, content_type = _download_image(session, src)
            if not data:
                img.decompose()
                continue
            state["counter"] += 1
            n = state["counter"]
            filename = f"images/img_{n}{_guess_ext(src, content_type)}"
            book.add_item(
                epub.EpubImage(
                    uid=f"img_{n}",
                    file_name=filename,
                    media_type=content_type or "image/jpeg",
                    content=data,
                )
            )
            state["urls"][src] = filename
        img["src"] = state["urls"][src]


def _build_chapter(book, entry, feed_title, session, index, style_item, state):
    title = entry.get("title") or "(untitled)"
    clean = sanitize_html(entry.get("_resolved_content", ""))

    soup = BeautifulSoup(clean, "lxml")
    _embed_images(book, soup, session, state)
    body_html = soup.body.decode_contents() if soup.body else str(soup)

    chapter = epub.EpubHtml(
        title=title, file_name=f"chapter_{index:04d}.xhtml", lang="en"
    )
    chapter.content = f"<h1>{_escape(title)}</h1>{_byline(entry, feed_title)}{body_html}"
    chapter.add_link(href=style_item.file_name, rel="stylesheet", type="text/css")
    return chapter


def build_epub(entries, feeds_by_id, session, out_dir, title=None) -> Path:
    today = date.today()
    title = title or f"Newspaper {today.isoformat()}"

    book = epub.EpubBook()
    book.set_identifier(f"feedpaper-{today.isoformat()}")
    book.set_title(title)
    book.set_language("en")
    book.add_author("Feedbin Newspaper")

    style_item = epub.EpubItem(
        uid="style",
        file_name="style/main.css",
        media_type="text/css",
        content=STYLE,
    )
    book.add_item(style_item)

    # Newest first; entries without a date sort last.
    ordered = sorted(entries, key=lambda e: e.get("published") or "", reverse=True)

    chapters = []
    state = {"urls": {}, "counter": 0}
    for index, entry in enumerate(ordered):
        feed_title = feeds_by_id.get(entry.get("feed_id"), "")
        chapter = _build_chapter(
            book, entry, feed_title, session, index, style_item, state
        )
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
