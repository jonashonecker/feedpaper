# How to install feedpaper on Windows

This guide shows how to install feedpaper from source in PowerShell and build your first
newspaper with it. A virtual environment keeps feedpaper and its Python packages apart
from the rest of your system.

You need Python 3.10 or newer, Git and a Feedbin account. The commands use Python 3.12.

## Install

1. Check that the Python launcher finds Python 3.12:

   ```powershell
   py -3.12 --version
   ```

2. Clone the repository, create a virtual environment and install feedpaper into it:

   ```powershell
   git clone https://github.com/jonashonecker/feedpaper.git
   cd feedpaper
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install .
   ```

   The commands use the virtual environment directly, so you don't need to activate it or
   change PowerShell's execution policy.

3. Check the install:

   ```powershell
   .\.venv\Scripts\feedpaper.exe --help
   ```

4. Build your first newspaper. `--keep-unread` leaves your posts unread in Feedbin:

   ```powershell
   .\.venv\Scripts\feedpaper.exe --keep-unread
   ```

   The first run asks for your Feedbin email and password and stores them in
   `$HOME\.config\feedpaper\config`. feedpaper writes the ePub to the current folder.

## Update

1. In the `feedpaper` folder, get the newest source:

   ```powershell
   git pull
   ```

2. Reinstall it into the existing virtual environment:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install .
   ```

## Related

- [How to build a standalone binary](/docs/how-to/build-a-binary.md) makes a folder that
  runs without a separate Python installation.
- [How to uninstall feedpaper](/docs/how-to/uninstall-feedpaper.md) removes it again.
