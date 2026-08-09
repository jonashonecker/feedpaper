# Set up feedpaper on your computer

In this tutorial you'll install the `feedpaper` command and connect it to your
Feedbin account. By the end you'll have a working `feedpaper` command, ready to
build your first newspaper in the
[next tutorial](/docs/tutorial/02-build-your-first-feedpaper.md).

## Before you start

You need a [Feedbin](https://feedbin.com) account and [Homebrew](https://brew.sh).
feedpaper ships as an Apple Silicon macOS binary.

## Step 1: Install feedpaper

```bash
brew install jonashonecker/tap/feedpaper
```

Homebrew puts `feedpaper` on your `PATH` without the macOS "unidentified developer"
warning, so there's nothing to unblock by hand.

## Step 2: Check the install

```bash
feedpaper --help
```

You'll see the usage message listing the available options. Your install works.
feedpaper asks for your Feedbin email and password the first time you build a
newspaper, so there's nothing else to set up now.

## What's next

Continue with
[Build your first newspaper](/docs/tutorial/02-build-your-first-feedpaper.md).

Prefer not to use Homebrew? See
[Install without Homebrew](/docs/how-to/install-without-homebrew.md).
