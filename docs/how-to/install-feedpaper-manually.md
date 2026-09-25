# Install feedpaper manually

Install feedpaper from source with Python instead of Homebrew.

You need Python 3.10 or newer and Git.

## Get the code and install it

### macOS and Linux

```bash
git clone https://github.com/jonashonecker/feedpaper.git
cd feedpaper
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

### Windows PowerShell

```powershell
git clone https://github.com/jonashonecker/feedpaper.git
cd feedpaper
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
```

On macOS and Linux, this puts a `feedpaper` command on your `PATH` while the virtual
environment is active. The Windows commands avoid activation and invoke feedpaper
directly, so they also work when PowerShell's execution policy blocks activation
scripts.

## Run it

On macOS and Linux:

```bash
feedpaper --help
```

On Windows:

```powershell
.\.venv\Scripts\feedpaper.exe --help
```

The first real run prompts for your Feedbin email and password and saves them to
`~/.config/feedpaper/config`, the same as the Homebrew install.

## Related

- The easy way: [Install feedpaper](/docs/tutorial/install-feedpaper.md)
- Windows instructions:
  [Install feedpaper on Windows](/docs/how-to/install-feedpaper-on-windows.md)
- Package a standalone binary:
  [Build a standalone binary](/docs/how-to/build-a-binary.md)
