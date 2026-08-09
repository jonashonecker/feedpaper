# Configuration files

## `config.txt`

feedpaper reads your Feedbin credentials from `config.txt` in the working directory.
It creates the file for you on first run, and you can edit it by hand later:

```
email = you@example.com
password = your-feedbin-password
```

feedpaper ignores blank lines and lines starting with `#`. Keep this file private:
it stores your password in plain text, and Git ignores it by default.

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
