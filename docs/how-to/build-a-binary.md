# Build a standalone binary

Produce a standalone `feedpaper` build for your machine, so it can run without a Python
install.

## Build it on macOS or Linux

From a source checkout with the build extra installed:

```bash
pip install -e ".[build]"
pyinstaller --onedir --name feedpaper feedpaper/__main__.py
```

PyInstaller writes the bundle to `dist/feedpaper/`: the `feedpaper` launcher plus an
`_internal/` folder of libraries. Keep them together.

Run it:

```bash
./dist/feedpaper/feedpaper --help
```

## Build it on Windows

From a source checkout in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[build]"
.\.venv\Scripts\pyinstaller.exe --onedir --name feedpaper feedpaper\__main__.py
```

PyInstaller writes `dist\feedpaper\feedpaper.exe` and its libraries. Keep the complete
`dist\feedpaper` folder together.

Run it:

```powershell
.\dist\feedpaper\feedpaper.exe --help
```

feedpaper reads its configuration from `~/.config/feedpaper/config`, the same as
running from source.

## Note

A PyInstaller build only runs on the operating system where you built it. Pushing a
version tag (`vX.Y.Z`) runs the `Release` GitHub Actions workflow, which builds macOS
and Windows bundles and attaches both to the release.

## Related

- Install from source: [Install feedpaper manually](/docs/how-to/install-feedpaper-manually.md)
