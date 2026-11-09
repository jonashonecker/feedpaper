# How to run the tests

This guide shows how to run the checks for a change locally, the same way the `Tests`
GitHub Actions workflow runs them on every pull request, and how to update the snapshot
tests after you change how posts render.

## Run the checks

1. In a source checkout, install feedpaper with its dev tools: pytest and the pyright
   type checker.

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

## Update the snapshots

The snapshot tests render one small post per feature from `tests/snapshots/<feature>.html`
and compare the result with `tests/snapshots/<feature>.expected.html`.

1. To cover a new feature, add its post as `tests/snapshots/<feature>.html`.

2. Rewrite the expected files:

   ```bash
   pytest tests/test_snapshots.py --update-snapshots
   ```

3. Check the diff of `tests/snapshots/` and confirm that only what you meant to change
   did.

## Related

- [How to install feedpaper manually](/docs/how-to/install-feedpaper-manually.md) sets up
  the source checkout.
