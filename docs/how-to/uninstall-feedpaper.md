# How to uninstall feedpaper

This guide shows how to remove feedpaper and its saved settings.

## Steps

1. Remove the program. With Homebrew:

   ```bash
   brew uninstall feedpaper
   ```

   For a manual install or a standalone bundle, delete the cloned `feedpaper` folder or
   the bundle's folder instead.

2. Delete `~/.config/feedpaper/`, where feedpaper keeps your email, password and
   excluded blogs. On macOS and Linux:

   ```bash
   rm -rf ~/.config/feedpaper
   ```

   On Windows, in PowerShell:

   ```powershell
   Remove-Item -Recurse -Force "$HOME\.config\feedpaper"
   ```
