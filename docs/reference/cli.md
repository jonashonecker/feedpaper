# Command-line interface

## Synopsis

```
feedpaper [-h] [-o OUTPUT] [--dry-run] [--keep-unread]
          [--exclude TITLE] [--exclude-file PATH] [--list-feeds]
```

## Options

| Option | Description | Default |
|---|---|---|
| `-h`, `--help` | Show the help message and exit. | — |
| `-o`, `--output DIR` | Directory where feedpaper writes the ePub. | `.` |
| `--dry-run` | Build the ePub without marking any posts as read. | off |
| `--keep-unread` | Build the ePub without marking any posts as read. | off |
| `--exclude TITLE` | Exclude a blog by feed title. You can repeat this flag. | none |
| `--exclude-file PATH` | File listing blog titles to exclude, one per line. | `excluded_feeds.txt` |
| `--list-feeds` | Print subscribed feeds as `feed_id<TAB>title`, sorted by title, then exit. | — |

## Output

On a successful build, feedpaper writes a file named `feedpaper-YYYY-MM-DD.epub` to
the output directory, where `YYYY-MM-DD` is the current date.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success, including when there are no unread posts to build. |
| `1` | An error occurred: missing credentials, a Feedbin API failure, or feedpaper built the ePub but couldn't mark posts as read. |
