# Build a newspaper without marking posts as read

Goal: produce an ePub while leaving every post unread on Feedbin.

By default a run marks the included posts as read once the ePub is written. To build
without changing your unread state, add one flag.

## Preview a build

```bash
newspaper --dry-run
```

Builds the ePub and skips marking anything as read. Use this to test your setup or
check the output.

## Keep posts unread on a real build

```bash
newspaper --keep-unread
```

Also builds the ePub without marking anything as read. Use it when you want a
newspaper copy but intend to keep the posts in your Feedbin queue.

Both flags leave every post unread. Run `newspaper` with neither to build and mark
the included posts as read.

## Related

- All options: [Command-line interface](/docs/reference/cli.md)
