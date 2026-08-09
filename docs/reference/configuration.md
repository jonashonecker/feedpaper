# Configuration files

## `.env`

feedpaper reads credentials from a `.env` file in the working directory.

| Key | Description |
|---|---|
| `FEEDBIN_EMAIL` | email address of the Feedbin account. |
| `FEEDBIN_PASSWORD` | Password of the Feedbin account. |

feedpaper needs both keys. `.env.example` provides a template.

## `excluded_feeds.txt`

A list of blogs to exclude from the newspaper. By default feedpaper looks for
`excluded_feeds.txt` in the working directory, and `--exclude-file` points it at
another path. `excluded_feeds.txt.example` provides a template, and Git ignores the
actual file.

Format:

- One feed title per line.
- feedpaper ignores blank lines and lines beginning with `#`.
- feedpaper matches titles case-insensitively against the feed title Feedbin
  reports, which `feedpaper --list-feeds` shows.

feedpaper combines titles passed with `--exclude` with the titles from this file.
