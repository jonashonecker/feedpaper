# Install feedpaper without Homebrew

Goal: install feedpaper straight from the release build when you don't use Homebrew.

## Download and extract

Open the [Releases page](https://github.com/jonashonecker/feedpaper/releases) and
download `feedpaper-macos.tar.gz`, then extract it:

```bash
tar -xzf feedpaper-macos.tar.gz
```

This gives you a `feedpaper/` folder with the launcher and its libraries. Keep them
together. The launcher needs the `_internal/` folder next to it.

## Install it

Move the folder to a stable location and link the launcher onto your `PATH`:

```bash
xattr -dr com.apple.quarantine feedpaper          # clears the download warning
sudo mv feedpaper /usr/local/opt/feedpaper
sudo ln -s /usr/local/opt/feedpaper/feedpaper /usr/local/bin/feedpaper
```

Then check it:

```bash
feedpaper --help
```

## Related

- The easier way:
  [Set up feedpaper on your computer](/docs/tutorial/01-set-up-feedpaper.md)
