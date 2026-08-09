# Build a standalone binary

Goal: produce a single-file `feedpaper` executable for your platform, so it can run
without a Python install.

## Build it

From a source checkout with the build extra installed:

```bash
pip install -e ".[build]"
pyinstaller --onefile --name feedpaper feedpaper/__main__.py
```

PyInstaller writes the executable to `dist/`:

- macOS / Linux → `dist/feedpaper`
- Windows → `dist/feedpaper.exe`

## Run it

```bash
./dist/feedpaper --help
```

The binary reads `config.txt` from the current working directory, the same as
running from source.

## Note

A PyInstaller binary only runs on the operating system where you built it. Pushing a
version tag (`vX.Y.Z`) runs the `Release` GitHub Actions workflow, which builds the
macOS binary and attaches it to the release.

## Related

- Run from a checkout: [Run feedpaper from source](/docs/how-to/run-from-source.md)
