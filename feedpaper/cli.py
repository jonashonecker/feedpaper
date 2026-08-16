from __future__ import annotations

import argparse
import sys
from dataclasses import replace

import requests

from feedpaper import __version__
from feedpaper.config import (
    SERVICE_FEEDBIN,
    ConfigError,
    config_path,
    load_config,
    save_config,
)
from feedpaper.content import count_lines, resolve_content
from feedpaper.epub_builder import build_epub
from feedpaper.exclusions import is_excluded, normalize_titles
from feedpaper.feedbin import FeedbinClient, FeedbinError
from feedpaper.freshrss import FreshRSSClient, FreshRSSError
from feedpaper.interactive import choose_excludes


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="feedpaper",
        description="Build an ePub newspaper from unread Feedbin or FreshRSS blog posts.",
    )
    parser.add_argument(
        "--version", action="version", version=f"feedpaper {__version__}"
    )
    parser.add_argument(
        "-o", "--output", default=".", help="Output directory (default: current dir)."
    )
    parser.add_argument(
        "--keep-unread",
        action="store_true",
        help="Build the ePub but do not mark entries as read.",
    )
    parser.add_argument(
        "--edit-excludes",
        action="store_true",
        help="Pick which blogs to exclude from a checklist and save them to the config.",
    )
    parser.add_argument(
        "--list-feeds",
        action="store_true",
        help="List your subscribed feeds (id and title) and exit.",
    )
    return parser.parse_args(argv)


def _edit_excludes(config, feeds_by_id) -> int:
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print("error: --edit-excludes needs an interactive terminal.", file=sys.stderr)
        return 1
    selected = choose_excludes(feeds_by_id, config.excluded)
    if selected is None:
        print("Cancelled; config unchanged.")
        return 0
    save_config(replace(config, excluded=tuple(selected)))
    print(f"Saved {len(selected)} excluded blog(s) to {config_path()}.")
    return 0


def main(argv=None) -> int:
    args = _parse_args(argv)

    try:
        config = load_config()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if config.service == SERVICE_FEEDBIN:
        client = FeedbinClient(config.email, config.password)
        service_name = "Feedbin"
    else:
        client = FreshRSSClient(config.url, config.user, config.password)
        service_name = "FreshRSS"

    try:
        client.verify()
        print(f"Authenticated with {service_name}.")

        feeds_by_id = client.get_feeds()

        if args.list_feeds:
            for feed_id, title in sorted(
                feeds_by_id.items(), key=lambda kv: (kv[1] or "").lower()
            ):
                print(f"{feed_id}\t{title}")
            return 0

        if args.edit_excludes:
            return _edit_excludes(config, feeds_by_id)

        excluded_titles = normalize_titles(config.excluded)

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

        if isinstance(client, FreshRSSClient) and config.fetch_full_content:
            short = [
                e for e in included if count_lines(e["_resolved_content"]) < config.min_lines
            ]
            if short:
                print(f"Fetching full article content for {len(short)} short post(s)...")
                for i, entry in enumerate(short, 1):
                    fetched = client.fetch_full_content(entry.get("url"))
                    title = entry.get("title") or "(untitled)"
                    if fetched and fetched.strip():
                        entry["_resolved_content"] = fetched
                        print(f"  [{i}/{len(short)}] fetched: {title}")
                    else:
                        print(
                            f"  [{i}/{len(short)}] kept short content (fetch failed or "
                            f"blocked by the site): {title}"
                        )

        print("Building ePub...")
        out_path = build_epub(included, feeds_by_id, client.session, args.output)
        print(f"Wrote {out_path}")
    except (FeedbinError, FreshRSSError, requests.RequestException) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    read_ids = [e["id"] for e in included]
    if args.keep_unread:
        print(
            f"Skipped marking as read (--keep-unread). "
            f"{len(read_ids)} post(s) stay unread."
        )
        return 0

    try:
        client.mark_as_read(read_ids)
        print(f"Marked {len(read_ids)} post(s) as read on {service_name}.")
    except (FeedbinError, FreshRSSError, requests.RequestException) as exc:
        print(f"warning: ePub built but failed to mark as read: {exc}", file=sys.stderr)
        return 1

    return 0
