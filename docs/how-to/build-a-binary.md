# How to build a standalone binary

This guide shows how to build a standalone `feedpaper` for your machine that runs without
a Python install.

A PyInstaller build only runs on the operating system where you built it.

## On macOS or Linux

1. In a source checkout, install feedpaper with the build extra:

   ```bash
   pip install -e ".[build]"
   ```

2. Build the bundle:

   ```bash
   pyinstaller --onedir --name feedpaper feedpaper/__main__.py
   ```

   PyInstaller writes the bundle to `dist/feedpaper/`: the `feedpaper` launcher and an
   `_internal/` folder of libraries. Keep them together.

3. Run it:

   ```bash
   ./dist/feedpaper/feedpaper --help
   ```

## On Windows

1. In a source checkout, open PowerShell and create a virtual environment with the
   build extra:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -e ".[build]"
   ```

2. Build the bundle:

   ```powershell
   .\.venv\Scripts\pyinstaller.exe --onedir --name feedpaper feedpaper\__main__.py
   ```

   PyInstaller writes `dist\feedpaper\feedpaper.exe` and its libraries. Keep the
   whole `dist\feedpaper` folder together.

3. Run it:

   ```powershell
   .\dist\feedpaper\feedpaper.exe --help
   ```

The bundle reads its configuration from `~/.config/feedpaper/config`, the same file as a
feedpaper installed from source.

## Related

- [How to install feedpaper manually](/docs/how-to/install-feedpaper-manually.md) sets up
  the source checkout.
- [How to release a new version](/docs/how-to/release-a-new-version.md) builds macOS and
  Windows bundles for a release in GitHub Actions.
