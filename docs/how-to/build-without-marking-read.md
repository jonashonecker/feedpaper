# Build a newspaper without marking posts as read

Goal: produce an ePub while leaving every post unread on Feedbin.

By default a run marks the included posts as read after it writes the ePub. To build
without changing your unread state, add `--keep-unread`:

```bash
feedpaper --keep-unread
```

feedpaper builds the ePub and skips marking anything as read. Use it to test your
setup, preview the output, or keep a copy while leaving the posts in your Feedbin
queue. Run `feedpaper` without the flag to build and mark the included posts as read.

## Related

- All options: [Command-line interface](/docs/reference/cli.md)
