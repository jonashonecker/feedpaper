# Uninstall feedpaper

Remove feedpaper and its saved settings.

## Remove the program

```bash
brew uninstall feedpaper
```

If you installed it manually, delete the checkout or the folder you moved the binary
into instead.

On Windows, delete the cloned `feedpaper` folder or the standalone bundle folder.

## Remove your credentials and settings

feedpaper keeps your email, password, and excluded blogs in `~/.config/feedpaper/`.
Delete that folder to remove them:

```bash
rm -rf ~/.config/feedpaper
```

On Windows PowerShell:

```powershell
Remove-Item -Recurse -Force "$HOME\.config\feedpaper"
```
