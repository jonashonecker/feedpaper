# Command-line interface

## Synopsis

```
feedpaper [-h] [--version] [-o OUTPUT] [--keep-unread]
          [--edit-excludes] [--list-feeds]
```

## Options

| Option | Description | Default |
|---|---|---|
| `-h`, `--help` | Show the help message and exit. | — |
| `--version` | Show the version and exit. | — |
| `-o`, `--output DIR` | Directory where feedpaper writes the ePub, created if it doesn't exist. | `.` |
| `--keep-unread` | Build the ePub without marking any posts as read. | off |
| `--edit-excludes` | Pick blogs to exclude from a checklist and save them to `config`. Needs an interactive terminal. | — |
| `--list-feeds` | Print subscribed feeds as `feed_id<TAB>title`, sorted by title, then exit. | — |

See [Configuration files](/docs/reference/configuration.md) for the `config` file
format.

## Output

On a successful build, feedpaper writes a file named `feedpaper-YYYY-MM-DD.epub` to
the output directory, where `YYYY-MM-DD` is the current date.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success, including when there are no unread posts to build. |
| `1` | An error occurred: missing credentials, a Feedbin or FreshRSS API failure, or feedpaper built the ePub but couldn't mark posts as read. |
| `2` | Invalid command-line usage, such as an unknown flag. |
