# Run the tests

Check a change locally the same way the `Tests` GitHub Actions workflow checks every pull
request.

## Install the dev tools

From a source checkout:

```bash
pip install -e ".[dev]"
```

This installs feedpaper with pytest and the pyright type checker.

## Run them

```bash
pytest
pyright
```

`pytest` runs the tests in `tests/`. None of them talk to Feedbin, so you don't need an
account or a network connection. `pyright` checks the types in `feedpaper/` and `tests/`.

## Note

The workflow runs both on Python 3.10, the oldest version feedpaper supports, and on
3.12, the version the release workflow builds the bundles with.

## Related

- Install from source: [Install feedpaper manually](/docs/how-to/install-feedpaper-manually.md)
