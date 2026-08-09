# newspaper

A small CLI that turns your **unread Feedbin blog posts** into an **ePub newspaper**
for your e-reader. It fetches all unread entries, builds a single ePub (one chapter
per post, images embedded for offline reading), and — only after the ePub is written
successfully — marks those entries as read on Feedbin.

For posts whose feed only ships a teaser, it falls back to Feedbin's built-in
full-content extraction (Mercury Parser).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
# then edit .env with your Feedbin email and password
```

## Usage

```bash
# Safe first run: build the ePub but keep everything unread
newspaper --dry-run

# Real run: build the ePub AND mark the posts as read on Feedbin
newspaper

# Write into a specific directory
newspaper --output ~/Reader

# Build without ever marking as read
newspaper --keep-unread
```

The output file is `newspaper-YYYY-MM-DD.epub`. Copy it to your e-reader
(e.g. XTeink X4) and read.

You can also run it without installing:

```bash
python -m newspaper --dry-run
```

## How it works

1. Authenticate against the Feedbin API (HTTP Basic auth from `.env`).
2. `GET /unread_entries.json` → all unread entry ids.
3. `GET /entries.json` (in batches of 100) → full entry data.
4. Per entry: use the inline `content`; if it's missing or looks truncated,
   fall back to `extracted_content_url`.
5. Build the ePub with embedded images.
6. `DELETE /unread_entries.json` (in batches of 1000) to mark as read —
   skipped on `--dry-run` / `--keep-unread`.
