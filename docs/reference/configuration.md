# Configuration files

## `.env`

Credentials are read from a `.env` file in the working directory.

| Key | Description |
|---|---|
| `FEEDBIN_EMAIL` | Email address of the Feedbin account. |
| `FEEDBIN_PASSWORD` | Password of the Feedbin account. |

Both keys are required. A template is provided in `.env.example`.

## `excluded_feeds.txt`

A list of blogs to exclude from the newspaper. The default path is
`excluded_feeds.txt` in the working directory; a different path can be set with
`--exclude-file`. A template is provided in `excluded_feeds.txt.example`, and the
file is git-ignored.

Format:

- One feed title per line.
- Blank lines and lines beginning with `#` are ignored.
- Titles are matched case-insensitively against the feed title reported by Feedbin
  (as listed by `newspaper --list-feeds`).

Titles passed with `--exclude` are combined with the titles from this file.
