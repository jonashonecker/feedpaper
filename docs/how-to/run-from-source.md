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

Run feedpaper once and it prompts for your email and password, or create the file
from the template:

```bash
cp config.txt.example config.txt
# edit config.txt and set email and password
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
