# Set up newspaper on your computer

In this tutorial you'll install the `newspaper` command and connect it to your
Feedbin account. By the end you'll have a working `newspaper` command, ready to
build your first newspaper in the
[next tutorial](/docs/tutorial/02-build-your-first-newspaper.md).

You don't need Python — the download is a self-contained program.

## Before you start

You need a [Feedbin](https://feedbin.com) account.

## Step 1 — Download the binary

Open the project's **Releases** page on GitHub
(`https://github.com/<owner>/<repo>/releases`) and download the file for your
operating system:

- macOS → `newspaper-macos`
- Linux → `newspaper-linux`
- Windows → `newspaper-windows.exe`

## Step 2 — Make it runnable

**macOS**

```bash
chmod +x newspaper-macos
xattr -d com.apple.quarantine newspaper-macos   # clears the download warning
sudo mv newspaper-macos /usr/local/bin/newspaper
```

**Linux**

```bash
chmod +x newspaper-linux
sudo mv newspaper-linux /usr/local/bin/newspaper
```

**Windows**

Rename `newspaper-windows.exe` to `newspaper.exe` and move it into a folder that's
on your `PATH`.

## Step 3 — Add your Feedbin credentials

In the folder where you'll run `newspaper`, create a file named `.env`:

```
FEEDBIN_EMAIL=you@example.com
FEEDBIN_PASSWORD=your-feedbin-password
```

## Step 4 — Check the install

```bash
newspaper --help
```

You'll see the usage message listing the available options. Your install works.

## What's next

Continue with
[Build your first newspaper](/docs/tutorial/02-build-your-first-newspaper.md).
