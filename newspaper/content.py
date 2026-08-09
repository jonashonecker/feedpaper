from __future__ import annotations

from bs4 import BeautifulSoup

# Tags removed entirely, including their content.
_STRIP_TAGS = ["script", "style", "iframe", "noscript", "object", "embed", "form"]

# Markers that suggest a feed only delivered a truncated teaser.
_TRUNCATION_MARKERS = (
    "read more",
    "continue reading",
    "read the rest",
    "read full",
    "weiterlesen",
)
_MIN_CONTENT_CHARS = 500


def _looks_truncated(html: str) -> bool:
    if not html or not html.strip():
        return True
    lowered = html.lower()
    if any(marker in lowered for marker in _TRUNCATION_MARKERS):
        return True
    text = BeautifulSoup(html, "lxml").get_text(strip=True)
    if len(text) < _MIN_CONTENT_CHARS:
        return True
    if text.rstrip().endswith(("…", "[…]", "[...]", "...")):
        return True
    return False


def resolve_content(client, entry) -> str:
    """Pick the best available content for an entry.

    Prefers the inline ``content``; falls back to Feedbin's full-content
    extraction only when the inline content is missing or looks truncated.
    """
    inline = entry.get("content") or ""
    if not _looks_truncated(inline):
        return inline
    extracted = client.get_extracted_content(entry.get("extracted_content_url"))
    if extracted and extracted.strip():
        return extracted
    return inline


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
