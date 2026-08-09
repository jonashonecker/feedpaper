from __future__ import annotations

import argparse
import sys

import requests

from newspaper.config import ConfigError, load_config
from newspaper.content import resolve_content
from newspaper.epub_builder import build_epub
from newspaper.exclusions import DEFAULT_EXCLUDE_FILE, is_excluded, load_excluded_titles
from newspaper.feedbin import FeedbinClient, FeedbinError


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="newspaper",
        description="Build an ePub newspaper from unread Feedbin blog posts.",
    )
    parser.add_argument(
        "-o", "--output", default=".", help="Output directory (default: current dir)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build the ePub but do not mark entries as read.",
    )
    parser.add_argument(
        "--keep-unread",
        action="store_true",
        help="Do not mark entries as read (keep them unread on Feedbin).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="TITLE",
        help="Feed title to exclude from the ePub (repeatable). "
        "Excluded posts stay unread on Feedbin.",
    )
    parser.add_argument(
        "--exclude-file",
        default=DEFAULT_EXCLUDE_FILE,
        help=f"File listing feed titles to exclude, one per line "
        f"(default: {DEFAULT_EXCLUDE_FILE}).",
    )
    parser.add_argument(
        "--list-feeds",
        action="store_true",
        help="List your subscribed feeds (id and title) and exit.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)

    try:
        config = load_config()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    client = FeedbinClient(config.email, config.password)

    try:
        client.verify()
        print("Authenticated with Feedbin.")

        feeds_by_id = client.get_feeds()

        if args.list_feeds:
            for feed_id, title in sorted(
                feeds_by_id.items(), key=lambda kv: (kv[1] or "").lower()
            ):
                print(f"{feed_id}\t{title}")
            return 0

        excluded_titles = load_excluded_titles(args.exclude_file, args.exclude)

        unread_ids = client.get_unread_ids()
        if not unread_ids:
            print("No unread posts. Nothing to do.")
            return 0
        print(f"Found {len(unread_ids)} unread post(s).")

        entries = client.get_entries(unread_ids)

        included, excluded = [], []
        for entry in entries:
            feed_title = feeds_by_id.get(entry.get("feed_id"), "")
            (excluded if is_excluded(feed_title, excluded_titles) else included).append(
                entry
            )

        if excluded:
            ex_titles = sorted(
                {feeds_by_id.get(e.get("feed_id"), "") for e in excluded}
            )
            print(
                f"Excluding {len(excluded)} post(s) from: "
                f"{', '.join(t for t in ex_titles if t)} (kept unread)."
            )

        if not included:
            print("All unread posts are from excluded feeds. Nothing to build.")
            return 0

        print("Resolving content...")
        for i, entry in enumerate(included, 1):
            entry["_resolved_content"] = resolve_content(client, entry)
            print(f"  [{i}/{len(included)}] {entry.get('title') or '(untitled)'}")

        print("Building ePub...")
        out_path = build_epub(included, feeds_by_id, client.session, args.output)
        print(f"Wrote {out_path}")
    except (FeedbinError, requests.RequestException) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    read_ids = [e["id"] for e in included]
    if args.dry_run or args.keep_unread:
        reason = "dry-run" if args.dry_run else "keep-unread"
        print(f"Skipped marking as read ({reason}). {len(read_ids)} post(s) stay unread.")
        return 0

    try:
        client.mark_as_read(read_ids)
        print(f"Marked {len(read_ids)} post(s) as read on Feedbin.")
    except (FeedbinError, requests.RequestException) as exc:
        print(f"warning: ePub built but failed to mark as read: {exc}", file=sys.stderr)
        return 1

    return 0
