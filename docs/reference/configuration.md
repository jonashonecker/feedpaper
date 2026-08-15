# Configuration files

## `config`

feedpaper stores your Feedbin credentials in `~/.config/feedpaper/config` (it honors
`$XDG_CONFIG_HOME`). On Windows this is
`%USERPROFILE%\.config\feedpaper\config`. It creates the file for you on first run,
and you can edit it by hand later:

```
email = you@example.com
password = your-feedbin-password
```

feedpaper ignores blank lines and lines starting with `#`. On systems that support
POSIX permissions, it writes the file with owner-only permissions, mode 600. On
Windows, the file inherits the access controls of your user profile. The plain-text
password lives in your home directory rather than in any project.

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
