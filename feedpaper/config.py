from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from getpass import getpass
from pathlib import Path

CONFIG_FILE = "config"

SERVICE_FEEDBIN = "feedbin"
SERVICE_FRESHRSS = "freshrss"
SERVICES = (SERVICE_FEEDBIN, SERVICE_FRESHRSS)

_EXCLUDE_HINT = (
    "\n# Exclude blogs from the newspaper. Use `feedpaper --edit-excludes` to pick\n"
    "# them, or add lines by hand (one per blog):\n"
    "# exclude = Hacker Newsletter\n"
)


class ConfigError(Exception):
    """Raised when required configuration is missing."""


@dataclass(frozen=True)
class Config:
    service: str = SERVICE_FEEDBIN
    email: str = ""  # Feedbin only
    password: str = ""  # Feedbin account password, or FreshRSS API password
    url: str = ""  # FreshRSS only: the Fever API endpoint (.../api/fever.php)
    user: str = ""  # FreshRSS only
    excluded: tuple[str, ...] = ()


def config_path() -> Path:
    """Path to the config file in the user's config directory.

    Honors ``$XDG_CONFIG_HOME`` and otherwise falls back to ``~/.config``.
    """
    base = os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")
    return Path(base) / "feedpaper" / CONFIG_FILE


def parse_config_file(path) -> Config:
    """Parse a ``key = value`` config file into a Config.

    Blank lines and lines starting with ``#`` are ignored. Keys are matched
    case-insensitively. ``exclude`` may appear multiple times (one blog title
    each). ``service`` selects the backend (``feedbin``, the default for configs
    written by older versions, or ``freshrss``); it determines which of
    ``email``/``password`` (Feedbin) or ``url``/``user``/``password`` (FreshRSS)
    are required.
    """
    service = SERVICE_FEEDBIN
    email = ""
    password = ""
    url = ""
    user = ""
    excluded: list[str] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().lower()
        value = value.strip()
        if key == "service":
            service = value.lower()
        elif key == "email":
            email = value
        elif key == "password":
            password = value
        elif key == "url":
            url = value
        elif key == "user":
            user = value
        elif key == "exclude" and value:
            excluded.append(value)

    if service not in SERVICES:
        raise ConfigError(
            f"{path} has an unknown service '{service}'. Expected one of: "
            f"{', '.join(SERVICES)}."
        )

    if service == SERVICE_FEEDBIN:
        required = (("email", email), ("password", password))
    else:
        required = (("url", url), ("user", user), ("password", password))

    missing = [name for name, value in required if not value]
    if missing:
        fields = ", ".join(f"'{name} = ...'" for name, _ in required)
        raise ConfigError(
            f"{path} is missing: {', '.join(missing)}. "
            f"Each line should read {fields}."
        )
    return Config(
        service=service,
        email=email,
        password=password,
        url=url,
        user=user,
        excluded=tuple(excluded),
    )


def save_config(config, path=None) -> None:
    """Write the config (credentials and any exclude lines) to ``path``."""
    path = Path(path) if path is not None else config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = ["# feedpaper configuration.", f"service = {config.service}"]
    if config.service == SERVICE_FEEDBIN:
        lines.append(f"email = {config.email}")
        lines.append(f"password = {config.password}")
    else:
        lines.append(f"url = {config.url}")
        lines.append(f"user = {config.user}")
        lines.append(f"password = {config.password}")
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


def _prompt_feedbin() -> Config:
    email = ""
    while not email:
        email = input("Feedbin email: ").strip()
    password = ""
    while not password:
        password = getpass("Feedbin password: ").strip()
    return Config(service=SERVICE_FEEDBIN, email=email, password=password)


def _prompt_freshrss() -> Config:
    url = ""
    while not url:
        url = input("FreshRSS Fever API URL (e.g. https://rss.example.net/api/fever.php): ").strip()
    user = ""
    while not user:
        user = input("FreshRSS username: ").strip()
    password = ""
    while not password:
        password = getpass("FreshRSS API password: ").strip()
    return Config(service=SERVICE_FRESHRSS, url=url, user=user, password=password)


def interactive_setup(path=None) -> Config:
    """Prompt once for credentials and save them to the config file."""
    path = Path(path) if path is not None else config_path()
    print(f"No config yet — let's set it up (saving to {path}).")

    service = ""
    while service not in SERVICES:
        service = input("Service (feedbin/freshrss): ").strip().lower()

    config = _prompt_feedbin() if service == SERVICE_FEEDBIN else _prompt_freshrss()
    save_config(config, path)
    print(f"Saved {path}.")
    return config


def load_config(path=None) -> Config:
    """Load service credentials from the user's config file.

    Reads an existing config; otherwise runs the interactive first-run prompt when
    in a terminal, and errors out when there's no way to ask.
    """
    path = Path(path) if path is not None else config_path()

    # Migrate a legacy config.txt written by earlier versions.
    legacy = path.parent / "config.txt"
    if legacy != path and legacy.exists() and not path.exists():
        legacy.rename(path)

    if path.exists():
        return parse_config_file(path)

    if sys.stdin.isatty() and sys.stdout.isatty():
        return interactive_setup(path)

    raise ConfigError(
        f"No config found at {path}. Run feedpaper in a terminal to set it up, "
        f"or create it with 'service = feedbin' (plus 'email' and 'password') or "
        f"'service = freshrss' (plus 'url', 'user', and 'password')."
    )
