# How to release a new version

This guide shows how to publish a new feedpaper version, so Homebrew users get it with
`brew upgrade`.

## Steps

1. Bump the version in `pyproject.toml` in a pull request, and merge it. The package reads
   the version at runtime, so there's nothing else to edit.
2. Tag the merge commit on `main` and push the tag:

   ```bash
   git checkout main && git pull
   git tag -a vX.Y.Z -m "feedpaper vX.Y.Z"
   git push origin vX.Y.Z
   ```

   The tag starts the `Release` GitHub Actions workflow. It builds the macOS and Windows
   bundles, attaches them to the GitHub release and updates the Homebrew tap formula
   with the `TAP_GITHUB_TOKEN` secret.

3. Check the result:
   - The **Actions** tab shows the `Release` workflow finishing green.
   - The release page lists `feedpaper-macos.tar.gz` and `feedpaper-windows-x64.zip`.
   - The `homebrew-tap` repository has a new `github-actions[bot]` commit bumping the
     formula.
   - `brew update && brew upgrade feedpaper` installs the new version.

## Related

- [How to build a standalone binary](/docs/how-to/build-a-binary.md) builds a bundle on
  your own machine.
