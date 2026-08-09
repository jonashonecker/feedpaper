# Exclude blogs from your newspaper

Goal: keep specific blogs out of your newspaper while leaving their posts unread on
Feedbin, so you can still read them elsewhere.

## Find the exact blog title

Matching is by feed title, so you need the title exactly as Feedbin knows it. List
all your subscribed blogs:

```bash
feedpaper --list-feeds
```

This prints every subscription as `feed_id<TAB>title`, sorted by title.

## Exclude blogs on every run

Create your personal exclusion list from the template. It stays local, and Git
ignores it:

```bash
cp excluded_feeds.txt.example excluded_feeds.txt
```

Add one blog title per line. feedpaper ignores blank lines and lines starting with
`#`, and matches titles case-insensitively:

```
# excluded_feeds.txt
Hacker Newsletter
neal.fun
```

Every run now skips those blogs.

## Exclude a blog for a single run

To skip a blog once without editing the file, use `--exclude`, which you can repeat:

```bash
feedpaper --exclude "Hacker Newsletter" --exclude "neal.fun"
```

## Use a different list file

```bash
feedpaper --exclude-file ~/configs/skip-these.txt
```

feedpaper combines titles from the file with any `--exclude` flags.

## Related

- Why those posts stay unread:
  [Content strategy](/docs/explanation/content-strategy.md)
- All options: [Command-line interface](/docs/reference/cli.md)
