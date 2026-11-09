import os
import stat
import sys

import pytest

from feedpaper import config as config_module
from feedpaper.config import (
    Config,
    ConfigError,
    config_path,
    load_config,
    parse_config_file,
    save_config,
)


def write(path, text):
    path.write_text(text, encoding="utf-8")
    return path


class TestParseConfigFile:
    def test_reads_email_password_and_excludes(self, tmp_path):
        path = write(
            tmp_path / "config",
            "email = me@example.com\n"
            "password = hunter2\n"
            "exclude = Hacker Newsletter\n"
            "exclude = Daring Fireball\n",
        )

        assert parse_config_file(path) == Config(
            email="me@example.com",
            password="hunter2",
            excluded=("Hacker Newsletter", "Daring Fireball"),
        )

    def test_ignores_comments_blank_lines_and_lines_without_equals(self, tmp_path):
        path = write(
            tmp_path / "config",
            "# a comment\n"
            "\n"
            "   \n"
            "not a setting\n"
            "email = me@example.com\n"
            "  # indented comment = still a comment\n"
            "password = hunter2\n",
        )

        assert parse_config_file(path) == Config("me@example.com", "hunter2")

    def test_keys_are_case_insensitive_and_whitespace_is_trimmed(self, tmp_path):
        path = write(
            tmp_path / "config",
            "  EMAIL=me@example.com  \nPassword   =   hunter2\nExclude= Some Blog \n",
        )

        assert parse_config_file(path) == Config(
            "me@example.com", "hunter2", ("Some Blog",)
        )

    def test_value_may_contain_equals_signs(self, tmp_path):
        path = write(tmp_path / "config", "email = me@example.com\npassword = a=b==c\n")

        assert parse_config_file(path).password == "a=b==c"

    def test_later_lines_win_for_single_value_keys(self, tmp_path):
        path = write(
            tmp_path / "config",
            "email = old@example.com\nemail = new@example.com\npassword = x\n",
        )

        assert parse_config_file(path).email == "new@example.com"

    def test_empty_exclude_lines_are_skipped(self, tmp_path):
        path = write(
            tmp_path / "config",
            "email = me@example.com\npassword = x\nexclude =\nexclude =   \n",
        )

        assert parse_config_file(path).excluded == ()

    def test_unknown_keys_are_ignored(self, tmp_path):
        path = write(
            tmp_path / "config", "email = me@example.com\npassword = x\ncolor = blue\n"
        )

        assert parse_config_file(path) == Config("me@example.com", "x")

    @pytest.mark.parametrize(
        ("text", "missing"),
        [
            ("password = x\n", "email"),
            ("email = me@example.com\n", "password"),
            ("email =\npassword =\n", "email, password"),
            ("", "email, password"),
        ],
    )
    def test_missing_credentials_raise(self, tmp_path, text, missing):
        path = write(tmp_path / "config", text)

        with pytest.raises(ConfigError, match=f"missing: {missing}\\."):
            parse_config_file(path)


class TestSaveConfig:
    def test_round_trips_with_excludes(self, tmp_path):
        path = tmp_path / "config"
        original = Config("me@example.com", "a=b#c", ("Blog One", "Blog Two"))

        save_config(original, path)

        assert parse_config_file(path) == original

    def test_writes_a_hint_when_nothing_is_excluded(self, tmp_path):
        path = tmp_path / "config"

        save_config(Config("me@example.com", "x"), path)

        text = path.read_text(encoding="utf-8")
        assert "# exclude = " in text
        assert parse_config_file(path).excluded == ()

    def test_creates_missing_parent_directories(self, tmp_path):
        path = tmp_path / "nested" / "feedpaper" / "config"

        save_config(Config("me@example.com", "x"), path)

        assert path.exists()

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX permissions only")
    def test_file_is_readable_by_the_owner_only(self, tmp_path):
        path = tmp_path / "config"

        save_config(Config("me@example.com", "x"), path)

        assert stat.S_IMODE(os.stat(path).st_mode) == 0o600

    def test_defaults_to_the_user_config_path(self, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

        save_config(Config("me@example.com", "x"))

        assert (tmp_path / "feedpaper" / "config").exists()


class TestConfigPath:
    def test_honors_xdg_config_home(self, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

        assert config_path() == tmp_path / "feedpaper" / "config"

    @pytest.mark.parametrize("value", [None, ""])
    def test_falls_back_to_dot_config(self, tmp_path, monkeypatch, value):
        if value is None:
            monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        else:
            monkeypatch.setenv("XDG_CONFIG_HOME", value)
        monkeypatch.setattr(config_module.Path, "home", lambda: tmp_path)

        assert config_path() == tmp_path / ".config" / "feedpaper" / "config"


class TestLoadConfig:
    def test_reads_an_existing_config(self, tmp_path):
        path = write(tmp_path / "config", "email = me@example.com\npassword = x\n")

        assert load_config(path) == Config("me@example.com", "x")

    def test_migrates_a_legacy_config_txt(self, tmp_path):
        legacy = write(
            tmp_path / "config.txt", "email = me@example.com\npassword = x\n"
        )
        path = tmp_path / "config"

        assert load_config(path) == Config("me@example.com", "x")
        assert path.exists()
        assert not legacy.exists()

    def test_does_not_overwrite_a_config_with_a_legacy_one(self, tmp_path):
        write(tmp_path / "config.txt", "email = old@example.com\npassword = x\n")
        path = write(tmp_path / "config", "email = new@example.com\npassword = x\n")

        assert load_config(path).email == "new@example.com"
        assert (tmp_path / "config.txt").exists()

    def test_without_a_terminal_a_missing_config_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False, raising=False)

        with pytest.raises(ConfigError, match="No config found"):
            load_config(tmp_path / "config")

    def test_in_a_terminal_a_missing_config_starts_setup(self, tmp_path, monkeypatch):
        path = tmp_path / "config"
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True, raising=False)
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True, raising=False)
        monkeypatch.setattr("builtins.input", lambda _prompt: "  me@example.com ")
        monkeypatch.setattr(config_module, "getpass", lambda _prompt: "hunter2")

        assert load_config(path) == Config("me@example.com", "hunter2")
        assert parse_config_file(path) == Config("me@example.com", "hunter2")
