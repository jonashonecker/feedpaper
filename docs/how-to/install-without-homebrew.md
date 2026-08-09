# Install feedpaper without Homebrew

Goal: install feedpaper straight from the release binary when you don't use Homebrew.

## Download the binary

Open the [Releases page](https://github.com/jonashonecker/feedpaper/releases) and
download `feedpaper-macos`.

## Make it runnable

```bash
chmod +x feedpaper-macos
xattr -d com.apple.quarantine feedpaper-macos   # clears the download warning
sudo mv feedpaper-macos /usr/local/bin/feedpaper
```

The `xattr` step clears the macOS download quarantine, so Gatekeeper stops blocking
the binary. Then check it:

```bash
feedpaper --help
```

## Related

- The easier way:
  [Set up feedpaper on your computer](/docs/tutorial/01-set-up-feedpaper.md)
