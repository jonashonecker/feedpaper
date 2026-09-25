# Install feedpaper on Windows

Install feedpaper from source in PowerShell. The virtual environment keeps feedpaper and
its Python packages isolated from the rest of your system.

## Before you start

You need:

- Python 3.10 or newer. Python 3.12 is used below.
- Git.
- A Feedbin account.

Check that the Python launcher is available:

```powershell
py -3.12 --version
```

## Install feedpaper

Clone the repository, create a virtual environment, and install the application:

```powershell
git clone https://github.com/jonashonecker/feedpaper.git
cd feedpaper
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
```

The commands use the virtual environment directly, so you do not need to activate it or
change PowerShell's execution policy.

## Check the install

```powershell
.\.venv\Scripts\feedpaper.exe --help
```

## Create your first newspaper

Start with `--keep-unread` so the first run does not change anything in Feedbin:

```powershell
.\.venv\Scripts\feedpaper.exe --keep-unread
```

The first run asks for your Feedbin email and password. It stores the configuration in
`$HOME\.config\feedpaper\config` and writes the ePub to the current directory.

## Update feedpaper

Pull the latest source and reinstall it into the existing environment:

```powershell
git pull
.\.venv\Scripts\python.exe -m pip install .
```

## Build a standalone executable

To create a folder you can run without a separate Python installation, see
[Build a standalone binary](/docs/how-to/build-a-binary.md).
