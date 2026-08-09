from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when required configuration is missing."""


@dataclass(frozen=True)
class Config:
    email: str
    password: str


def load_config() -> Config:
    """Load Feedbin credentials from a local .env file / environment."""
    load_dotenv()
    email = os.getenv("FEEDBIN_EMAIL", "").strip()
    password = os.getenv("FEEDBIN_PASSWORD", "").strip()

    missing = [
        name
        for name, value in (("FEEDBIN_EMAIL", email), ("FEEDBIN_PASSWORD", password))
        if not value
    ]
    if missing:
        raise ConfigError(
            "Missing required setting(s): "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill in your Feedbin credentials."
        )
    return Config(email=email, password=password)
