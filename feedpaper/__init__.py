"""Build an ePub newspaper from unread Feedbin blog posts."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("feedpaper")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "0.0.0+unknown"
