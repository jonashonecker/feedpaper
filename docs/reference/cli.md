# Command-line interface

## Synopsis

```
newspaper [-h] [-o OUTPUT] [--dry-run] [--keep-unread]
          [--exclude TITLE] [--exclude-file PATH] [--list-feeds]
```

## Options

| Option | Description | Default |
|---|---|---|
| `-h`, `--help` | Show the help message and exit. | — |
| `-o`, `--output DIR` | Directory the ePub is written to. | `.` |
| `--dry-run` | Build the ePub without marking any posts as read. | off |
| `--keep-unread` | Build the ePub without marking any posts as read. | off |
| `--exclude TITLE` | Exclude a blog by feed title. May be given multiple times. | none |
| `--exclude-file PATH` | File listing blog titles to exclude, one per line. | `excluded_feeds.txt` |
| `--list-feeds` | Print subscribed feeds as `feed_id<TAB>title`, sorted by title, then exit. | — |

## Output

On a successful build a file named `newspaper-YYYY-MM-DD.epub` is written to the
output directory, where `YYYY-MM-DD` is the current date.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success, including when there are no unread posts to build. |
| `1` | An error occurred: missing credentials, a Feedbin API failure, or the ePub was built but marking posts as read failed. |
