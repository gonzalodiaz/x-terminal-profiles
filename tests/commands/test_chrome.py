"""Tests for xtp.commands.chrome."""

from __future__ import annotations

import json

from xtp.commands.chrome import get_chrome_profiles


class TestGetChromeProfiles:
    def test_missing_file_returns_empty(self, tmp_path, monkeypatch):
        import xtp.commands.chrome as mod
        monkeypatch.setattr(mod, "CHROME_LOCAL_STATE", tmp_path / "nope")
        assert get_chrome_profiles() == []

    def test_valid_json_parsed(self, tmp_path, monkeypatch):
        import xtp.commands.chrome as mod

        local_state = tmp_path / "Local State"
        local_state.write_text(json.dumps({
            "profile": {
                "info_cache": {
                    "Default": {"name": "Person 1"},
                    "Profile 1": {"name": "Work"},
                }
            }
        }))
        monkeypatch.setattr(mod, "CHROME_LOCAL_STATE", local_state)
        profiles = get_chrome_profiles()
        assert len(profiles) == 2
        dirs = [p[0] for p in profiles]
        assert "Default" in dirs
        assert "Profile 1" in dirs
