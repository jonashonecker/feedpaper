# Configuration files

## `config`

feedpaper stores your Feedbin credentials in `~/.config/feedpaper/config` (it
honors `$XDG_CONFIG_HOME`). It creates the file for you on first run, and you can edit
it by hand later:

```
email = you@example.com
password = your-feedbin-password
```

feedpaper ignores blank lines and lines starting with `#`. It writes the file with
owner-only permissions, mode 600, so only your account can read the plain-text
password, and it lives in your home directory rather than in any project.

If you used an older version, feedpaper renames a legacy `config.txt` to `config`
automatically on first run.

To change your credentials, edit `email` or `password` in the file. Or delete the file,
and feedpaper prompts you for new ones on the next run.

### Excluding blogs

Add an `exclude` line for each blog you want to keep out of the newspaper:

```
exclude = Hacker Newsletter
exclude = neal.fun
```

feedpaper matches these titles case-insensitively against your subscribed blogs.
`feedpaper --edit-excludes` lets you pick them from a checklist instead. Excluded
blogs stay unread on Feedbin.

## Removing feedpaper

Uninstall with `brew uninstall feedpaper`. To remove your saved credentials too, delete
the configuration directory:

```bash
rm -rf ~/.config/feedpaper
```
