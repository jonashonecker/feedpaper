# How to run the tests

This guide shows how to run the checks for a change locally, the same way the `Tests`
GitHub Actions workflow runs them on every pull request.

## Steps

1. In a source checkout, install feedpaper with the dev tools, pytest and the pyright
   type checker:

   ```bash
   pip install -e ".[dev]"
   ```

2. Run the tests:

   ```bash
   pytest
   ```

   They cover the code in `feedpaper/` without talking to Feedbin, so they need neither
   an account nor a network connection.

3. Check the types in `feedpaper/` and `tests/`:

   ```bash
   pyright
   ```

The workflow runs both on Python 3.10, the oldest version feedpaper supports, and on
3.12, the version the release bundles use.

## Related

- [How to install feedpaper manually](/docs/how-to/install-feedpaper-manually.md) sets up
  the source checkout.
