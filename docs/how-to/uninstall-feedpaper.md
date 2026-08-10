# Uninstall feedpaper

Remove feedpaper and its saved settings from your Mac.

## Remove the program

```bash
brew uninstall feedpaper
```

If you installed it manually, delete the checkout or the folder you moved the binary
into instead.

## Remove your credentials and settings

feedpaper keeps your email, password, and excluded blogs in `~/.config/feedpaper/`.
Delete that folder to remove them:

```bash
rm -rf ~/.config/feedpaper
```
