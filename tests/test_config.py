"""Tests for xtp.config — uses tmp_path fixtures."""

from __future__ import annotations

import pytest

from xtp import config


class TestPaths:
    def test_profile_dir(self, profiles_dir):
        assert config.profile_dir("foo") == profiles_dir / "foo"

    def test_profile_toml(self, profiles_dir):
        assert config.profile_toml("foo") == profiles_dir / "foo" / "profile.toml"


class TestListProfiles:
    def test_empty_dir(self, profiles_dir):
        assert config.list_profiles() == []

    def test_ignores_dirs_without_toml(self, profiles_dir):
        (profiles_dir / "empty").mkdir()
        assert config.list_profiles() == []

    def test_returns_sorted(self, fake_profile):
        fake_profile("zebra", {"name": "z"})
        fake_profile("alpha", {"name": "a"})
        assert config.list_profiles() == ["alpha", "zebra"]


class TestLoadSaveProfile:
    def test_load_missing_raises(self, profiles_dir):
        with pytest.raises(FileNotFoundError):
            config.load_profile("nonexistent")

    def test_round_trip(self, profiles_dir):
        data = {"name": "test", "git": {"author_name": "Alice"}}
        config.save_profile("test", data)
        loaded = config.load_profile("test")
        assert loaded == data


class TestEnsureProfileDirs:
    def test_creates_subdirs(self, profiles_dir):
        (profiles_dir / "myprof").mkdir()
        config.ensure_profile_dirs("myprof")
        pdir = profiles_dir / "myprof"
        assert (pdir / "claude").is_dir()
        assert (pdir / "gh").is_dir()
        assert (pdir / "aws").is_dir()


class TestBuildEnv:
    def test_minimal(self, fake_profile):
        fake_profile("min", {"name": "min"})
        env = config.build_env("min")
        assert env["XTP_PROFILE"] == "min"
        assert "CLAUDE_CONFIG_DIR" in env
        assert "GH_CONFIG_DIR" in env

    def test_git_section(self, fake_profile):
        fake_profile("dev", {
            "git": {"author_name": "Alice", "author_email": "a@b.c"},
        })
        env = config.build_env("dev")
        assert env["GIT_AUTHOR_NAME"] == "Alice"
        assert env["GIT_COMMITTER_NAME"] == "Alice"
        assert env["GIT_AUTHOR_EMAIL"] == "a@b.c"

    def test_ssh_key_tilde_expansion(self, fake_profile):
        fake_profile("ssh", {
            "git": {"ssh_key": "~/.ssh/id_ed25519"},
        })
        env = config.build_env("ssh")
        assert "~" not in env["GIT_SSH_COMMAND"]
        assert "id_ed25519" in env["GIT_SSH_COMMAND"]

    def test_chrome_sets_browser(self, fake_profile):
        fake_profile("chrome", {
            "chrome": {"profile_directory": "Profile 1"},
        })
        env = config.build_env("chrome")
        assert env["BROWSER"].endswith("browser.sh")

    def test_aws_profile(self, fake_profile):
        fake_profile("awstest", {
            "aws": {"profile": "staging"},
        })
        env = config.build_env("awstest")
        assert env["AWS_PROFILE"] == "staging"
        assert "AWS_CONFIG_FILE" in env

    def test_npm_isolate(self, fake_profile):
        fake_profile("npmtest", {
            "npm": {"isolate": True},
        })
        env = config.build_env("npmtest")
        assert env["NPM_CONFIG_USERCONFIG"].endswith("npmrc")

    def test_custom_env_vars(self, fake_profile):
        fake_profile("custom", {
            "env": {"MY_VAR": "hello", "MY_PATH": "~/stuff"},
        })
        env = config.build_env("custom")
        assert env["MY_VAR"] == "hello"
        assert "~" not in env["MY_PATH"]


class TestGenerateBrowserScript:
    def test_creates_executable_script(self, fake_profile):
        fake_profile("browser", {
            "chrome": {"profile_directory": "Profile 2"},
        })
        config.generate_browser_script("browser")
        script = config.profile_dir("browser") / "browser.sh"
        assert script.is_file()
        assert script.stat().st_mode & 0o755
        content = script.read_text()
        assert "Profile 2" in content
        assert "#!/bin/bash" in content

    def test_no_chrome_config_does_nothing(self, fake_profile):
        fake_profile("nochrome", {"name": "x"})
        config.generate_browser_script("nochrome")
        assert not (config.profile_dir("nochrome") / "browser.sh").exists()
