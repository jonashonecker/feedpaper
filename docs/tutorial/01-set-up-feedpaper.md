# Set up feedpaper on your computer

In this tutorial you'll install the `feedpaper` command and connect it to your
Feedbin account. By the end you'll have a working `feedpaper` command, ready to
build your first newspaper in the
[next tutorial](/docs/tutorial/02-build-your-first-feedpaper.md).

You don't need Python—the download is a self-contained program.

## Before you start

You need a [Feedbin](https://feedbin.com) account.

## Step 1: Download the binary

Open the project's **Releases** page on GitHub
(`https://github.com/jonashonecker/feedpaper/releases`) and download the file for your
operating system:

- macOS → `feedpaper-macos`
- Linux → `feedpaper-linux`
- Windows → `feedpaper-windows.exe`

## Step 2: Make it runnable

**macOS**

```bash
chmod +x feedpaper-macos
xattr -d com.apple.quarantine feedpaper-macos   # clears the download warning
sudo mv feedpaper-macos /usr/local/bin/feedpaper
```

**Linux**

```bash
chmod +x feedpaper-linux
sudo mv feedpaper-linux /usr/local/bin/feedpaper
```

**Windows**

Rename `feedpaper-windows.exe` to `feedpaper.exe` and move it into a folder that's
on your `PATH`.

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
