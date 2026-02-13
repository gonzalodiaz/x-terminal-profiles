"""Tests for xtp.commands.show."""

from __future__ import annotations

import pytest

from xtp.commands.show import run


class TestShow:
    def test_profile_not_found_exits_1(self, profiles_dir):
        with pytest.raises(SystemExit) as exc_info:
            run("nonexistent")
        assert exc_info.value.code == 1

    def test_valid_profile_prints_info(self, fake_profile, capsys):
        fake_profile("demo", {
            "name": "demo",
            "git": {"author_name": "Bob", "author_email": "bob@test.com"},
        })
        run("demo")
        output = capsys.readouterr().out
        assert "Profile: demo" in output
        assert "Bob" in output
        assert "Environment variables:" in output
