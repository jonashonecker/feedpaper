from __future__ import annotations

import argparse
import sys
from dataclasses import replace

from feedpaper import __version__
from feedpaper.client import ClientError
from feedpaper.config import ConfigError, config_path, load_config, save_config
from feedpaper.exclusions import is_excluded, normalize_titles
from feedpaper.feedbin import FeedbinClient
from feedpaper.interactive import choose_excludes
from feedpaper.render import render_epub


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="feedpaper",
        description="Build an ePub newspaper from unread Feedbin blog posts.",
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
        help="Build the ePub but do not mark entries as read on Feedbin.",
    )
    parser.add_argument(
        "--edit-excludes",
        action="store_true",
        help="Pick which blogs to exclude from a checklist and save them to the config.",
    )
    parser.add_argument(
        "--list-feeds",
        action="store_true",
        help="List the titles of your subscribed feeds and exit.",
    )
    return parser.parse_args(argv)


def _edit_excludes(config, feed_titles) -> int:
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print("error: --edit-excludes needs an interactive terminal.", file=sys.stderr)
        return 1
    selected = choose_excludes(feed_titles, config.excluded)
    if selected is None:
        print("Cancelled; config unchanged.")
        return 0
    save_config(replace(config, excluded=tuple(selected)))
    print(f"Saved {len(selected)} excluded blog(s) to {config_path()}.")
    return 0


def _report_progress(done, total, title) -> None:
    if done == 0:
        if total:
            print(f"Found {total} unread post(s).")
            print("Resolving content...")
        return
    print(f"  [{done}/{total}] {title}")


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

        if args.list_feeds:
            for title in client.feed_titles():
                print(title)
            return 0

        if args.edit_excludes:
            return _edit_excludes(config, client.feed_titles())

        articles = client.fetch_unread(progress=_report_progress)
        if not articles:
            print("No unread posts. Nothing to do.")
            return 0

        excluded_titles = normalize_titles(config.excluded)
        included, excluded = [], []
        for article in articles:
            target = (
                excluded
                if is_excluded(article.feed_title, excluded_titles)
                else included
            )
            target.append(article)

        if excluded:
            ex_titles = sorted({a.feed_title for a in excluded if a.feed_title})
            print(
                f"Excluding {len(excluded)} post(s) from: "
                f"{', '.join(ex_titles)} (kept unread)."
            )

        if not included:
            print("All unread posts are from excluded feeds. Nothing to build.")
            return 0

        print("Building ePub...")
        out_path = render_epub(included, args.output)
        print(f"Wrote {out_path}")
    except ClientError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.keep_unread:
        print(
            f"Skipped marking as read (--keep-unread). "
            f"{len(included)} post(s) stay unread."
        )
        return 0

    try:
        client.mark_as_read(included)
        print(f"Marked {len(included)} post(s) as read on Feedbin.")
    except ClientError as exc:
        print(f"warning: ePub built but failed to mark as read: {exc}", file=sys.stderr)
        return 1

    return 0
