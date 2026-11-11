from __future__ import annotations

import argparse
import sys
from dataclasses import replace

from feedpaper import __version__
from feedpaper.config import ConfigError, config_path, load_config, save_config
from feedpaper.feedbin import FeedbinAdapter
from feedpaper.interactive import choose_excludes
from feedpaper.newspaper import Reporter, build_newspaper
from feedpaper.service import FeedService, FeedServiceError


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


class _ConsoleReporter(Reporter):
    """Prints each step of building the newspaper as it happens."""

    def found(self, count: int) -> None:
        if count:
            print(f"Found {count} unread post(s).")
        else:
            print("No unread posts. Nothing to do.")

    def excluded(self, count: int, feed_titles: list[str]) -> None:
        print(
            f"Excluding {count} post(s) from: {', '.join(feed_titles)} (kept unread)."
        )

    def resolving(self, count: int) -> None:
        print("Resolving content...")

    def resolved(self, done: int, total: int, title: str) -> None:
        print(f"  [{done}/{total}] {title}")

    def rendering(self) -> None:
        print("Building ePub...")


def main(argv=None) -> int:
    args = _parse_args(argv)

    try:
        config = load_config()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    service: FeedService = FeedbinAdapter(config.email, config.password)

    try:
        service.verify()
        print("Authenticated with Feedbin.")

        if args.list_feeds:
            for title in service.feed_titles():
                print(title)
            return 0

        if args.edit_excludes:
            return _edit_excludes(config, service.feed_titles())

        newspaper = build_newspaper(
            service,
            args.output,
            excluded_blogs=config.excluded,
            keep_unread=args.keep_unread,
            reporter=_ConsoleReporter(),
        )
    except FeedServiceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if newspaper.path is None:
        if newspaper.found:
            print("All unread posts are from excluded feeds. Nothing to build.")
        return 0
    print(f"Wrote {newspaper.path}")

    count = len(newspaper.articles)
    if newspaper.mark_error:
        print(
            f"warning: ePub built but failed to mark as read: {newspaper.mark_error}",
            file=sys.stderr,
        )
        return 1
    if newspaper.marked_read:
        print(f"Marked {count} post(s) as read on Feedbin.")
    else:
        print(f"Skipped marking as read (--keep-unread). {count} post(s) stay unread.")
    return 0
