# Set up newspaper on your computer

In this tutorial you'll install `newspaper` and connect it to your Feedbin account.
By the end you'll have a working command on your computer, ready to build your first
newspaper in the [next tutorial](/docs/tutorial/02-build-your-first-newspaper.md).

## Before you start

You need:

- Python 3.10 or newer
- A [Feedbin](https://feedbin.com) account

## Step 1 — Create a virtual environment

From the project directory, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Step 2 — Install newspaper

```bash
pip install -e .
```

This gives you a `newspaper` command inside the activated environment.

## Step 3 — Add your Feedbin credentials

Copy the template and open the new file:

```bash
cp .env.example .env
```

Fill in your Feedbin email and password:

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
