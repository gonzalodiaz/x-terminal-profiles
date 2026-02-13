"""Tests for xtp.commands.delete."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from xtp.commands.delete import run


class TestDelete:
    def test_missing_profile_exits_1(self, profiles_dir):
        with pytest.raises(SystemExit) as exc_info:
            run("nonexistent")
        assert exc_info.value.code == 1

    def test_confirm_y_deletes(self, fake_profile):
        pdir = fake_profile("doomed", {"name": "doomed"})
        with patch("builtins.input", return_value="y"):
            run("doomed")
        assert not pdir.is_dir()

    def test_confirm_n_cancels(self, fake_profile, capsys):
        pdir = fake_profile("safe", {"name": "safe"})
        with patch("builtins.input", return_value="n"):
            run("safe")
        assert pdir.is_dir()
        assert "Cancelled" in capsys.readouterr().out
