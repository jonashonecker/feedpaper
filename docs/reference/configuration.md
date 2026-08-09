# Configuration files

## `config.txt`

feedpaper stores your Feedbin credentials in `~/.config/feedpaper/config.txt` (it
honors `$XDG_CONFIG_HOME`). It creates the file for you on first run, and you can edit
it by hand later:

```
email = you@example.com
password = your-feedbin-password
```

feedpaper ignores blank lines and lines starting with `#`. Keep this file private:
it stores your password in plain text, and Git ignores it by default.

### Excluding blogs

Add an `exclude` line for each blog you want to keep out of the newspaper:

```
exclude = Hacker Newsletter
exclude = neal.fun
```

feedpaper matches these titles case-insensitively against your subscribed blogs.
`feedpaper --edit-excludes` lets you pick them from a checklist instead. Excluded
blogs stay unread on Feedbin.
