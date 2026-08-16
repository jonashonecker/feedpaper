# Why excluding blogs helps

feedpaper turns every unread post into a chapter. That works well for long-form writing,
but some feeds don't belong in a newspaper you read on an e-reader.

## Feeds that read badly on an e-reader

- **Link digests.** Newsletters like a "links of the week" roundup are mostly URLs. On
  an e-ink reader you can't follow the links, so the chapter is just a dead list.
- **Media posts.** Video and podcast feeds carry almost no readable text. The content is
  a player you'd open on your phone or computer.
- **Script-heavy posts.** Some posts rely on JavaScript to render their content.
  feedpaper strips scripts for a clean, offline read, so these can come out sparse.

## What excluding does

When you exclude a blog, feedpaper leaves its posts out of the ePub and keeps them
unread on your service. You don't lose anything: you still see those posts in Feedbin or
FreshRSS and can read them where they suit you, usually your phone. Your newspaper stays
focused on the long-form writing that reads well on the e-reader.

Pick the blogs to exclude with `feedpaper --edit-excludes`. See
[Build your first newspaper](/docs/tutorial/build-your-first-newspaper.md).
