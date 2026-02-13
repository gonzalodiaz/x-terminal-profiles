"""List all profiles."""

from __future__ import annotations

import os

from xtp import config


def run() -> None:
    profiles = config.list_profiles()
    if not profiles:
        print("No profiles found. Create one with: xtp create <name>")
        return

    active = os.environ.get("XTP_PROFILE", "")
    for name in profiles:
        try:
            cfg = config.load_profile(name)
            desc = cfg.get("profile", {}).get("description", "")
        except Exception:
            desc = ""

        marker = " *" if name == active else ""
        desc_part = f"  ({desc})" if desc else ""
        print(f"  {name}{marker}{desc_part}")

    if active:
        print(f"\n* = active profile")
