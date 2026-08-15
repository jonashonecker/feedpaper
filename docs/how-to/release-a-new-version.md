# Release a new version

Publish a new feedpaper version so Homebrew users get it with `brew upgrade`.

## Steps

1. Bump the version in `pyproject.toml`. The package reads it at runtime, so there's
   nothing else to edit.
2. Commit the bump and push `main`.
3. Tag the release and push the tag:

   ```bash
   git tag -a vX.Y.Z -m "feedpaper vX.Y.Z"
   git push origin vX.Y.Z
   ```

The `Release` GitHub Actions workflow does the rest: it builds macOS and Windows
bundles, attaches them to the GitHub release, and updates the Homebrew tap formula
automatically with the `TAP_GITHUB_TOKEN` secret.

## Verify

- The **Actions** tab shows the `Release` workflow finishing green.
- The release page lists `feedpaper-macos.tar.gz` and
  `feedpaper-windows-x64.zip`.
- The `homebrew-tap` repository has a new `github-actions[bot]` commit bumping the formula.
- `brew update && brew upgrade feedpaper` installs the new version.

## Related

- Build a bundle locally: [Build a standalone binary](/docs/how-to/build-a-binary.md)
