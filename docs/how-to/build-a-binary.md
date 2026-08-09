# Build a standalone binary

Goal: produce a single-file `newspaper` executable for your platform, so it can run
without a Python install.

## Build it

From a source checkout with the build extra installed:

```bash
pip install -e ".[build]"
pyinstaller --onefile --name newspaper newspaper/__main__.py
```

The executable is written to `dist/`:

- macOS / Linux → `dist/newspaper`
- Windows → `dist/newspaper.exe`

## Run it

```bash
./dist/newspaper --help
```

The binary reads `.env` and `excluded_feeds.txt` from the current working
directory, the same as running from source.

## Note

A PyInstaller binary only runs on the operating system it was built on. To produce
binaries for macOS, Linux and Windows at once, push a version tag (`vX.Y.Z`) — the
`Release` GitHub Actions workflow builds all three and attaches them to the release.

## Related

- Run from a checkout: [Run newspaper from source](/docs/how-to/run-from-source.md)
