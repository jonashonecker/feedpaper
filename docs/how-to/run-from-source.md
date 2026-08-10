# Run feedpaper from source

Goal: run `feedpaper` from a Python checkout instead of a downloaded binary—for
example to modify it or work on it.

You need Python 3.10 or newer.

## Install into a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Add your credentials

The first time you run feedpaper, it prompts for your Feedbin email and password and
saves them to `~/.config/feedpaper/config`.

## Run it

```bash
feedpaper --keep-unread
```

You can also run it without installing the console script:

```bash
python -m feedpaper --keep-unread
```

## Related

- All options: [Command-line interface](/docs/reference/cli.md)
- Package a binary: [Build a standalone binary](/docs/how-to/build-a-binary.md)
