# Set up feedpaper on your computer

In this tutorial you'll install the `feedpaper` command and connect it to your
Feedbin account. By the end you'll have a working `feedpaper` command, ready to
build your first newspaper in the
[next tutorial](/docs/tutorial/02-build-your-first-feedpaper.md).

You don't need Python—the download is a self-contained program.

## Before you start

You need a [Feedbin](https://feedbin.com) account. feedpaper ships as an Apple
Silicon macOS binary.

## Step 1: Download the binary

Open the project's **Releases** page on GitHub
(`https://github.com/jonashonecker/feedpaper/releases`) and download `feedpaper-macos`.

## Step 2: Make it runnable

```bash
chmod +x feedpaper-macos
xattr -d com.apple.quarantine feedpaper-macos   # clears the download warning
sudo mv feedpaper-macos /usr/local/bin/feedpaper
```

## Step 3: Check the install

```bash
feedpaper --help
```

You'll see the usage message listing the available options. Your install works.
feedpaper asks for your Feedbin email and password the first time you build a
newspaper, so there's nothing else to set up now.

## What's next

Continue with
[Build your first newspaper](/docs/tutorial/02-build-your-first-feedpaper.md).
