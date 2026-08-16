# Configuration files

## `config`

feedpaper stores your credentials in `~/.config/feedpaper/config` (it honors
`$XDG_CONFIG_HOME`). It creates the file for you on first run, and you can edit it by
hand later. The first line that matters is `service`, which selects the backend:
`feedbin` or `freshrss`. Configs written by feedpaper versions before FreshRSS support
have no `service` line; feedpaper treats those as `feedbin`.

feedpaper ignores blank lines and lines starting with `#`. It writes the file with
owner-only permissions, mode 600, so only your account can read the plain-text
password, and it lives in your home directory rather than in any project.

If you used an older version, feedpaper renames a legacy `config.txt` to `config`
automatically on first run.

### Feedbin

```
service = feedbin
email = you@example.com
password = your-feedbin-password
```

### FreshRSS

```
service = freshrss
url = https://rss.example.net/api/fever.php
user = your-freshrss-username
password = your-freshrss-api-password
fetch_full_content = false
min_lines = 4
```

`url` is your FreshRSS instance's Fever API endpoint, not your account login page.
feedpaper needs the `password` to be the **API password**, not your regular FreshRSS
login password:

1. In FreshRSS, enable "Allow API access (required for mobile apps)" under
   **Settings → Authentication**.
2. Set an "API password (e.g., for mobile apps)" under **Settings → Profile**. FreshRSS
   shows your API address (ending in `api/fever.php` or `api/greader.php`, depending on
   the client) right next to it — use the `fever.php` one for `url`.

See FreshRSS's own [mobile access
docs](https://freshrss.github.io/FreshRSS/en/users/06_Mobile_access.html) for more.

feedpaper uses FreshRSS's [Fever-compatible
API](https://freshrss.github.io/FreshRSS/en/developers/06_Fever_API.html), not the
Google Reader-compatible one, since it covers everything feedpaper needs (unread posts,
content, marking as read) with a simpler request/response shape.

#### Fetching full articles

The Fever API has no full-text-extraction endpoint, so short or teaser-only posts stay
short in the newspaper by default. Set `fetch_full_content = true` to have feedpaper
fetch the linked article page itself and extract its main content whenever a post's
inline content has fewer than `min_lines` lines of text (default `4`). This is off by
default since it makes an extra request per short post and its extraction is a
heuristic, not a full readability engine. See [Content strategy](/docs/explanation/content-strategy.md)
for details and trade-offs.

### Changing credentials

To change your credentials, edit the relevant lines in the file. Or delete the file,
and feedpaper prompts you for new ones on the next run — first asking which service to
use.

### Excluding blogs

Add an `exclude` line for each blog you want to keep out of the newspaper:

```
exclude = Hacker Newsletter
exclude = neal.fun
```

feedpaper matches these titles case-insensitively against your subscribed blogs.
`feedpaper --edit-excludes` lets you pick them from a checklist instead. Excluded
blogs stay unread on Feedbin or FreshRSS.
