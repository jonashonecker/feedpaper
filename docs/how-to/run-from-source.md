# Run feedpaper from source

Goal: run `feedpaper` from a Python checkout instead of a downloaded binary — for
example to modify it or work on it.

You need Python 3.10 or newer.

## Install into a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Add your credentials

```bash
cp .env.example .env
# edit .env and set FEEDBIN_EMAIL and FEEDBIN_PASSWORD
```

## Run it

```bash
feedpaper --dry-run
```

You can also run it without installing the console script:

```bash
python -m feedpaper --dry-run
```

## Related

- All options: [Command-line interface](/docs/reference/cli.md)
- Package a binary: [Build a standalone binary](/docs/how-to/build-a-binary.md)
