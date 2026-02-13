"""Shared fixtures for xtp tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def profiles_dir(tmp_path, monkeypatch):
    """Redirect xtp.config paths to a temp directory."""
    import xtp.config as cfg

    config_dir = tmp_path / "config"
    profiles = config_dir / "profiles"
    profiles.mkdir(parents=True)

    monkeypatch.setattr(cfg, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(cfg, "PROFILES_DIR", profiles)
    return profiles


@pytest.fixture()
def fake_profile(profiles_dir):
    """Factory fixture: create a profile with given TOML content."""
    from xtp import toml_writer

    def _create(name: str, data: dict) -> Path:
        pdir = profiles_dir / name
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / "profile.toml").write_text(toml_writer.dumps(data))
        return pdir

    return _create
