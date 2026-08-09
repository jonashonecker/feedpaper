# Content strategy: inline content vs. full-text extraction

Feeds don't all deliver the same thing. This page explains how `feedpaper` decides
what text ends up in each chapter, and why.

## The partial-feed problem

Feedbin gives every entry a `content` field, but its completeness depends on the
publisher. Some blogs syndicate the whole article; others ship only a teaser — a
first paragraph and a "Read more" link — expecting you to open the site. If the tool
naively used `content`, those posts would land in the newspaper truncated.

## Prefer inline content, fall back to extraction

So `feedpaper` prefers the inline `content` and only reaches for a fallback when
that content looks incomplete. The fallback is Feedbin's own full-text extraction:
every entry carries an `extracted_content_url` — a pre-signed endpoint backed by
Mercury Parser that fetches the original page and returns cleaned full-text HTML.
Because Feedbin already does this server-side, the tool never scrapes anything
itself.

The decision, per post:

1. Take the inline `content`.
2. If it's missing or looks truncated, fetch the extracted content instead.
3. If extraction fails or comes back empty, keep whatever inline content there was.

## What "looks truncated" means

The truncation check is deliberately simple. Inline content is treated as incomplete
when it is empty, shorter than about 500 characters of text, contains a
"read more" / "continue reading" / "weiterlesen" style marker, or ends with an
ellipsis. This favours full articles without making an extra network request for
every post.

## Trade-offs

The heuristic can occasionally be wrong — a genuinely short post might trigger an
unnecessary extraction, and an unusually worded teaser might slip through. It is
tuned to be cheap and predictable rather than perfect. The thresholds live in
`feedpaper/content.py` and are easy to adjust; a future refinement could let you
mark specific blogs as "always extract".
