# Build a standalone binary

Goal: produce a standalone `feedpaper` build for your machine, so it can run without a
Python install.

## Build it

From a source checkout with the build extra installed:

```bash
pip install -e ".[build]"
pyinstaller --onedir --name feedpaper feedpaper/__main__.py
```

PyInstaller writes the bundle to `dist/feedpaper/`: the `feedpaper` launcher plus an
`_internal/` folder of libraries. Keep them together.

## Run it

```bash
./dist/feedpaper/feedpaper --help
```

feedpaper reads its configuration from `~/.config/feedpaper/config.txt`, the same as
running from source.

## Note

A PyInstaller build only runs on the operating system where you built it. Pushing a
version tag (`vX.Y.Z`) runs the `Release` GitHub Actions workflow, which builds the
macOS bundle and attaches it to the release.

## Related

- Run from a checkout: [Run feedpaper from source](/docs/how-to/run-from-source.md)
