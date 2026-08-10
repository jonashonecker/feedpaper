# Build your first newspaper

In this tutorial you'll turn your unread Feedbin posts into an ePub, choose which blogs
to include, and open it on your e-reader. By the end you'll have a newspaper file on
your device.

## Before you start

Install feedpaper first. See [Install feedpaper](/docs/tutorial/install-feedpaper.md).
Open a terminal in the folder where you want the newspaper saved, and make sure you have
a few unread posts in Feedbin.

## Connect to Feedbin

The first time you run feedpaper, it asks for your Feedbin email and password and saves
them to `~/.config/feedpaper/config`. Trigger that now by listing your blogs:

```bash
feedpaper --list-feeds
```

feedpaper prompts for your email and password, keeping the password hidden, then prints
the blogs you're subscribed to.

## Choose which blogs to skip

Some blogs don't read well as an ePub: link-only newsletters, or video and podcast feeds
you'd rather open on your phone. Pick the ones to leave out:

```bash
feedpaper --edit-excludes
```

feedpaper shows your blogs as a checklist. Use the arrow keys to move, space to tick a
blog you want to skip, and enter to save. Excluded blogs stay unread on Feedbin, so you
can still read them elsewhere. You can also edit the `exclude` lines in
`~/.config/feedpaper/config` by hand.

For when this helps, see
[Why excluding blogs helps](/docs/explanation/why-exclude-blogs.md).

## Build the ePub

For your first build, add `--keep-unread`. It creates the ePub without changing anything
in Feedbin:

```bash
feedpaper --keep-unread
```

feedpaper fetches your unread posts, skips the blogs you excluded, and writes a file
named `feedpaper-YYYY-MM-DD.epub` into the current directory.

## Open the newspaper

Open the `.epub` on your computer with any ePub reader. On macOS, Books works. You'll
see one chapter per post, newest first. Each post has a byline and inline images.

## Copy it to your e-reader

Transfer the `.epub` to your e-reader, for example the XTeink X4, the way you normally
copy files, and open it. You're reading your first newspaper.

## Do a real build

Now run it without `--keep-unread`:

```bash
feedpaper
```

This builds the newspaper again and marks the included posts as read in Feedbin, so next
time you only get what's new.
