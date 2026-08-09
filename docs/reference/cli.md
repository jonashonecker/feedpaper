# Command-line interface

## Synopsis

```
feedpaper [-h] [-o OUTPUT] [--keep-unread]
          [--edit-excludes] [--list-feeds]
```

## Options

| Option | Description | Default |
|---|---|---|
| `-h`, `--help` | Show the help message and exit. | — |
| `-o`, `--output DIR` | Directory where feedpaper writes the ePub. | `.` |
| `--keep-unread` | Build the ePub without marking any posts as read. | off |
| `--edit-excludes` | Pick blogs to exclude from a checklist and save them to `config.txt`. | — |
| `--list-feeds` | Print subscribed feeds as `feed_id<TAB>title`, sorted by title, then exit. | — |

## Output

On a successful build, feedpaper writes a file named `feedpaper-YYYY-MM-DD.epub` to
the output directory, where `YYYY-MM-DD` is the current date.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success, including when there are no unread posts to build. |
| `1` | An error occurred: missing credentials, a Feedbin API failure, or feedpaper built the ePub but couldn't mark posts as read. |
