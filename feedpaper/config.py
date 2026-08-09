from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from getpass import getpass
from pathlib import Path

CONFIG_FILE = "config.txt"

_EXCLUDE_HINT = (
    "\n# Exclude blogs from the newspaper. Use `feedpaper --edit-excludes` to pick\n"
    "# them, or add lines by hand (one per blog):\n"
    "# exclude = Hacker Newsletter\n"
)


class ConfigError(Exception):
    """Raised when required configuration is missing."""


@dataclass(frozen=True)
class Config:
    email: str
    password: str
    excluded: tuple[str, ...] = ()


def config_path() -> Path:
    """Path to config.txt in the user's config directory.

    Honors ``$XDG_CONFIG_HOME`` and otherwise falls back to ``~/.config``.
    """
    base = os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")
    return Path(base) / "feedpaper" / CONFIG_FILE


def parse_config_file(path) -> Config:
    """Parse a ``key = value`` config file into a Config.

    Blank lines and lines starting with ``#`` are ignored. Keys are matched
    case-insensitively; ``email`` and ``password`` are required, and ``exclude``
    may appear multiple times (one blog title each).
    """
    email = ""
    password = ""
    excluded: list[str] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().lower()
        value = value.strip()
        if key == "email":
            email = value
        elif key == "password":
            password = value
        elif key == "exclude" and value:
            excluded.append(value)

    missing = [
        name for name, value in (("email", email), ("password", password)) if not value
    ]
    if missing:
        raise ConfigError(
            f"{path} is missing: {', '.join(missing)}. "
            f"Each line should read 'email = ...' or 'password = ...'."
        )
    return Config(email=email, password=password, excluded=tuple(excluded))


def save_config(config, path=None) -> None:
    """Write the config (email, password, and any exclude lines) to ``path``."""
    path = Path(path) if path is not None else config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# feedpaper configuration.",
        f"email = {config.email}",
        f"password = {config.password}",
    ]
    text = "\n".join(lines) + "\n"
    if config.excluded:
        text += "\n" + "".join(f"exclude = {title}\n" for title in config.excluded)
    else:
        text += _EXCLUDE_HINT
    path.write_text(text, encoding="utf-8")
    # The file holds a password, so restrict it to the owner.
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def interactive_setup(path=None) -> Config:
    """Prompt once for credentials and save them to the config file."""
    path = Path(path) if path is not None else config_path()
    print(f"No config yet — let's set it up (saving to {path}).")
    email = ""
    while not email:
        email = input("Feedbin email: ").strip()
    password = ""
    while not password:
        password = getpass("Feedbin password: ").strip()

    config = Config(email=email, password=password)
    save_config(config, path)
    print(f"Saved {path}.")
    return config


def load_config(path=None) -> Config:
    """Load Feedbin credentials from the user's config.txt.

    Reads an existing config; otherwise runs the interactive first-run prompt when
    in a terminal, and errors out when there's no way to ask.
    """
    path = Path(path) if path is not None else config_path()
    if path.exists():
        return parse_config_file(path)

    if sys.stdin.isatty() and sys.stdout.isatty():
        return interactive_setup(path)

    raise ConfigError(
        f"No config found at {path}. Run feedpaper in a terminal to set it up, "
        f"or create it with 'email = ...' and 'password = ...'."
    )
