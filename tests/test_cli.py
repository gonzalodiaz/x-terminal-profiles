"""Tests for xtp.cli — CLI dispatch tests."""

from __future__ import annotations

import subprocess
import sys
from unittest.mock import patch

import pytest

from xtp.cli import main


class TestVersion:
    def test_version_flag(self, capsys):
        with pytest.raises(SystemExit, match="0"):
            with patch("sys.argv", ["xtp", "--version"]):
                main()
        assert "xtp" in capsys.readouterr().out


class TestNoSubcommand:
    def test_no_args_exits_1(self):
        with pytest.raises(SystemExit) as exc_info:
            with patch("sys.argv", ["xtp"]):
                main()
        assert exc_info.value.code == 1


class TestShowDispatch:
    def test_show_no_name_no_env_exits_1(self, capsys, monkeypatch):
        monkeypatch.delenv("XTP_PROFILE", raising=False)
        with pytest.raises(SystemExit) as exc_info:
            with patch("sys.argv", ["xtp", "show"]):
                main()
        assert exc_info.value.code == 1
        assert "no profile name" in capsys.readouterr().err.lower()

    def test_show_uses_env_var(self, monkeypatch, profiles_dir, fake_profile):
        fake_profile("envprof", {"name": "envprof"})
        monkeypatch.setenv("XTP_PROFILE", "envprof")
        with patch("sys.argv", ["xtp", "show"]):
            main()  # should not raise


class TestCurrent:
    def test_current_with_profile(self, capsys, monkeypatch):
        monkeypatch.setenv("XTP_PROFILE", "myprof")
        with patch("sys.argv", ["xtp", "current"]):
            main()
        assert "myprof" in capsys.readouterr().out

    def test_current_without_profile(self, capsys, monkeypatch):
        monkeypatch.delenv("XTP_PROFILE", raising=False)
        with patch("sys.argv", ["xtp", "current"]):
            main()
        assert "none" in capsys.readouterr().out
