# Build your first newspaper

In this tutorial you'll turn your unread Feedbin posts into an ePub and open it on
your e-reader. By the end you'll have a newspaper file on your device.

## Before you start

Complete [Set up newspaper on your computer](/docs/tutorial/01-set-up-newspaper.md)
first, then activate your virtual environment:

```bash
source .venv/bin/activate
```

Make sure you have a few unread posts in Feedbin.

## Step 1 — Build the ePub

For your first build, add `--dry-run`. It creates the ePub without changing
anything in Feedbin:

```bash
newspaper --dry-run
```

You'll watch it authenticate, fetch your unread posts, and write a file named
`newspaper-YYYY-MM-DD.epub` into the current directory.

## Step 2 — Open the newspaper

Open the `.epub` on your computer with any ePub reader (on macOS, Books works). You
will see one chapter per post, newest first, each with a byline (author · blog ·
date · source link) and images inline.

## Step 3 — Copy it to your e-reader

Transfer the `.epub` to your e-reader (for example the XTeink X4) the way you
normally copy files, and open it. You're reading your first newspaper.

## Step 4 — Do a real build

Now run it without `--dry-run`:

```bash
newspaper
```

This builds the newspaper again and marks the included posts as read in Feedbin, so
next time you only get what's new.

## What's next

- Skip blogs that don't read well as an ePub:
  [Exclude blogs from your newspaper](/docs/how-to/exclude-blogs.md)
- Look up every option: [Command-line interface](/docs/reference/cli.md)
