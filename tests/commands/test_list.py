"""Tests for xtp.commands.list."""

from __future__ import annotations

from xtp.commands.list import run


class TestList:
    def test_no_profiles(self, profiles_dir, capsys):
        run()
        assert "No profiles found" in capsys.readouterr().out

    def test_active_profile_marked(self, fake_profile, capsys, monkeypatch):
        fake_profile("alpha", {"name": "alpha"})
        fake_profile("beta", {"name": "beta"})
        monkeypatch.setenv("XTP_PROFILE", "alpha")
        run()
        output = capsys.readouterr().out
        assert "alpha *" in output
        assert "beta" in output
        assert "* = active profile" in output
