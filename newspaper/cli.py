from __future__ import annotations

import argparse
import sys

import requests

from newspaper.config import ConfigError, load_config
from newspaper.content import resolve_content
from newspaper.epub_builder import build_epub
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

        unread_ids = client.get_unread_ids()
        if not unread_ids:
            print("No unread posts. Nothing to do.")
            return 0
        print(f"Found {len(unread_ids)} unread post(s).")

        entries = client.get_entries(unread_ids)
        feeds_by_id = client.get_feeds()

        print("Resolving content...")
        for i, entry in enumerate(entries, 1):
            entry["_resolved_content"] = resolve_content(client, entry)
            print(f"  [{i}/{len(entries)}] {entry.get('title') or '(untitled)'}")

        print("Building ePub...")
        out_path = build_epub(entries, feeds_by_id, client.session, args.output)
        print(f"Wrote {out_path}")
    except (FeedbinError, requests.RequestException) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    read_ids = [e["id"] for e in entries]
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
