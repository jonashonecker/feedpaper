# Build your first newspaper

In this tutorial you'll turn your unread Feedbin posts into an ePub and open it on
your e-reader. By the end you'll have a newspaper file on your device.

## Before you start

Complete [Set up feedpaper on your computer](/docs/tutorial/01-set-up-feedpaper.md)
first, so the `feedpaper` command works. Open a terminal in the folder where you
want the newspaper saved, and make sure you have a few unread posts in Feedbin.

## Step 1: Build the ePub

For your first build, add `--keep-unread`. It creates the ePub without changing
anything in Feedbin:

```bash
feedpaper --keep-unread
```

The first time you run feedpaper, it asks for your Feedbin email and password and
saves them to `~/.config/feedpaper/config`. Then it authenticates, fetches your unread
posts, and
writes a file named `feedpaper-YYYY-MM-DD.epub` into the current directory.

## Step 2: Open the newspaper

Open the `.epub` on your computer with any ePub reader. On macOS, Books works.
You'll see one chapter per post, newest first, each with a byline—author · blog ·
date · source link—and images inline.

## Step 3: Copy it to your e-reader

Transfer the `.epub` to your e-reader, for example the XTeink X4, the way you
normally copy files, and open it. You're reading your first newspaper.

## Step 4: Do a real build

Now run it without `--keep-unread`:

```bash
feedpaper
```

This builds the newspaper again and marks the included posts as read in Feedbin, so
next time you only get what's new.

## What's next

- Skip blogs that don't read well as an ePub:
  [Exclude blogs from your newspaper](/docs/how-to/exclude-blogs.md)
- Look up every option: [Command-line interface](/docs/reference/cli.md)
