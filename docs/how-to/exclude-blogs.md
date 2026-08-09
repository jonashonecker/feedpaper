# Exclude blogs from your newspaper

Goal: keep specific blogs out of your newspaper while leaving their posts unread on
Feedbin, so you can still read them elsewhere.

## Pick blogs from a checklist

Run:

```bash
feedpaper --edit-excludes
```

feedpaper shows your subscribed blogs as a checklist and pre-ticks the ones you
already exclude. Use the arrow keys to move, space to toggle a blog, and enter to
save. feedpaper writes your choice to `config.txt`.

## Edit the list by hand

You can also add blogs directly in `config.txt`, one `exclude` line per blog:

```
exclude = Hacker Newsletter
exclude = neal.fun
```

feedpaper matches these titles case-insensitively against your subscribed blogs.

## Related

- Why those posts stay unread:
  [Content strategy](/docs/explanation/content-strategy.md)
- All options: [Command-line interface](/docs/reference/cli.md)
