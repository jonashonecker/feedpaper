# Install feedpaper

In this tutorial you'll install the `feedpaper` command with Homebrew, ready to build
your first newspaper in the
[next tutorial](/docs/tutorial/build-your-first-newspaper.md).

## Before you start

You need a [Feedbin](https://feedbin.com) account and [Homebrew](https://brew.sh).
feedpaper ships as an Apple Silicon macOS binary.

## Install with Homebrew

```bash
brew install jonashonecker/tap/feedpaper
```

Homebrew puts `feedpaper` on your `PATH` without the macOS "unidentified developer"
warning, so there's nothing to unblock by hand.

## Check the install

```bash
feedpaper --help
```

You'll see the usage message listing the available options. Your install works.

## What's next

Continue with
[Build your first newspaper](/docs/tutorial/build-your-first-newspaper.md).

Prefer not to use Homebrew? See
[Install feedpaper manually](/docs/how-to/install-feedpaper-manually.md).
