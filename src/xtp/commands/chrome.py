"""Chrome profile discovery."""

from __future__ import annotations

import json
from pathlib import Path


CHROME_LOCAL_STATE = (
    Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Local State"
)


def get_chrome_profiles() -> list[tuple[str, str]]:
    """Return list of (directory_name, display_name) for Chrome profiles."""
    if not CHROME_LOCAL_STATE.is_file():
        return []

    try:
        data = json.loads(CHROME_LOCAL_STATE.read_text())
        info_cache = data.get("profile", {}).get("info_cache", {})
        profiles = []
        for directory, info in sorted(info_cache.items()):
            display_name = info.get("name", directory)
            profiles.append((directory, display_name))
        return profiles
    except (json.JSONDecodeError, KeyError):
        return []


def run() -> None:
    profiles = get_chrome_profiles()
    if not profiles:
        print("No Chrome profiles found.")
        print(f"Looked in: {CHROME_LOCAL_STATE}")
        return

    print("Chrome profiles:")
    for directory, display_name in profiles:
        print(f"  {directory}: {display_name}")
