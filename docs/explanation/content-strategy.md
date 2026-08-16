# Content strategy: inline content vs. full-text extraction

Feeds don't all deliver the same thing. This page explains how `feedpaper` decides
what text ends up in each chapter, and why.

## The partial-feed problem

Both Feedbin and FreshRSS give every entry a `content` field, but its completeness
depends on the publisher. Some blogs syndicate the whole article. Others ship only a
teaser—a first paragraph and a "Read more" link—expecting you to open the site. If the
tool naively used `content`, those posts would land in the newspaper truncated.

## Prefer inline content, fall back to extraction

So `feedpaper` prefers the inline content and only reaches for a fallback when it looks
incomplete. On Feedbin, every entry carries an `extracted_content_url`—a pre-signed
endpoint backed by Mercury Parser that fetches the original page and returns cleaned
full-text HTML. Because Feedbin already does this server-side, the tool never scrapes
anything itself for that path.

FreshRSS has no per-request equivalent of `extracted_content_url`, so by default
feedpaper uses the inline FreshRSS content as-is. If a feed reads truncated in your
newspaper, FreshRSS's own [website-scraping
rules](https://freshrss.github.io/FreshRSS/en/users/11_website_scraping.html), set up
per-feed on the FreshRSS side, are the primary way to fix it—whatever they produce
lands in `content` before feedpaper ever sees the entry.

As an opt-in alternative for FreshRSS, setting `fetch_full_content = true` (see
[Configuration files](/docs/reference/configuration.md)) makes feedpaper scrape the
linked article page itself—unlike the Feedbin path, this fetch and extraction happens
in feedpaper, not a server-side service—whenever the inline content has fewer than
`min_lines` lines of text. It looks for an `<article>` / `<main>` element, or falls
back to the page's largest text block, then hands whatever it finds through the same
sanitizer as everything else.

The decision, per post:

1. Take the inline content.
2. On Feedbin, if it's missing or looks truncated (see below), fetch the extracted
   content instead.
3. On FreshRSS, if `fetch_full_content` is enabled and the inline content has fewer
   than `min_lines` lines, fetch and extract the linked article page instead.
4. If extraction fails, comes back empty, or isn't attempted, keep whatever inline
   content there was.

## What "looks truncated" means

The truncation check is deliberately simple. feedpaper treats inline content as
incomplete when it's empty, shorter than about 500 characters of text, contains a
"read more" / "continue reading" / "weiterlesen" style marker, or ends with an
ellipsis. This favours full articles without making an extra network request for
every post.

## Trade-offs

The heuristic can occasionally be wrong—a genuinely short post might trigger an
unnecessary extraction, and an unusually worded teaser might slip through. It aims
for cheap, predictable behaviour rather than perfection. The thresholds live in
`feedpaper/content.py`, and adjusting them is easy. A future refinement could let you
mark specific blogs as "always extract."

The FreshRSS full-article fetch has the same kind of trade-off, plus two more specific
to scraping a page directly rather than using a server-side extraction service: it
adds a network request per short post, and its "biggest text block" heuristic (in
`feedpaper/freshrss.py`) can occasionally grab the wrong element on an unusually laid
out page. That's why it's opt-in rather than the default.

## Related

- [Build your first newspaper](/docs/tutorial/build-your-first-newspaper.md)
