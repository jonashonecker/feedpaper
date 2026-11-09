# Build your first newspaper

In this tutorial you'll turn your unread Feedbin posts into an ePub, choose which blogs
to include, and open it on your e-reader. By the end you'll have a newspaper file on
your device.

## Before you start

Install feedpaper first, as shown in [Install feedpaper](/docs/tutorial/install-feedpaper.md).
Make sure you have a few unread posts in Feedbin.

## Connect and choose your blogs

1. Open a terminal in the folder where you want the newspaper saved.

2. Let's connect feedpaper to Feedbin by listing your blogs:

   ```bash
   feedpaper --list-feeds
   ```

   The first time you run feedpaper, it asks for your Feedbin email and password, keeping
   the password hidden, and saves them to `~/.config/feedpaper/config`. You'll see the
   blogs you're subscribed to.

3. Some blogs don't read well as an ePub, such as link-only newsletters or video and
   podcast feeds you'd rather open on your phone. Let's leave those out:

   ```bash
   feedpaper --edit-excludes
   ```

   You'll see your blogs as a checklist. Use the arrow keys to move, space to tick a blog
   you want to skip, and enter to save. Excluded blogs stay unread on Feedbin, so you
   still find them there.

## Build and read the newspaper

1. For the first build, we'll add `--keep-unread`, so feedpaper creates the ePub without
   changing anything in Feedbin:

   ```bash
   feedpaper --keep-unread
   ```

   feedpaper fetches your unread posts, skips the blogs you excluded, and writes a file
   named `feedpaper-YYYY-MM-DD.epub` into the current folder.

2. Open the `.epub` on your computer with an ePub reader, such as Books on macOS. You'll
   see one chapter per post, newest first, each with a byline and its images.

3. Copy the `.epub` to your e-reader, for example the XTeink X4, the way you normally
   copy files to it, and open it there. You're reading your first newspaper.

## Make it a habit

1. From now on, run feedpaper without `--keep-unread`:

   ```bash
   feedpaper
   ```

   You'll get the newspaper again, and feedpaper marks the included posts as read in
   Feedbin. Next time, only what's new ends up in the newspaper.

## What's next

[Why excluding blogs helps](/docs/explanation/why-exclude-blogs.md) explains which blogs
are worth leaving out.
