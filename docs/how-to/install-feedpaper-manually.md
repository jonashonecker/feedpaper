# How to install feedpaper manually

This guide shows how to install feedpaper from source with Python instead of Homebrew.

You need Python 3.10 or newer and Git.

## On macOS and Linux

1. Get the code:

   ```bash
   git clone https://github.com/jonashonecker/feedpaper.git
   cd feedpaper
   ```

2. Create a virtual environment, activate it and install feedpaper into it:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install .
   ```

3. Check the install:

   ```bash
   feedpaper --help
   ```

The `feedpaper` command is on your `PATH` while the virtual environment is active.

## On Windows

1. Get the code in PowerShell:

   ```powershell
   git clone https://github.com/jonashonecker/feedpaper.git
   cd feedpaper
   ```

2. Create a virtual environment and install feedpaper into it:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install .
   ```

3. Check the install:

   ```powershell
   .\.venv\Scripts\feedpaper.exe --help
   ```

These commands call the virtual environment's programs directly instead of activating
it, so they also work when PowerShell's execution policy blocks activation scripts.

## Next

The first real run asks for your Feedbin email and password and saves them to
`~/.config/feedpaper/config`, the same as the Homebrew install.

## Related

- [Install feedpaper](/docs/tutorial/install-feedpaper.md) is the tutorial for the
  Homebrew install.
- [How to install feedpaper on Windows](/docs/how-to/install-feedpaper-on-windows.md) goes
  from install to first newspaper on Windows.
- [How to build a standalone binary](/docs/how-to/build-a-binary.md) packages feedpaper so
  it runs without Python.
