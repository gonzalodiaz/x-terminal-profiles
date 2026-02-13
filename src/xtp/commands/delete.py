"""Delete a profile."""

from __future__ import annotations

import shutil

from xtp import config


def run(name: str) -> None:
    pdir = config.profile_dir(name)
    if not pdir.is_dir():
        print(f"Error: Profile '{name}' not found.")
        raise SystemExit(1)

    print(f"This will delete: {pdir}")
    confirm = input(f"Delete profile '{name}'? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    shutil.rmtree(pdir)
    print(f"Profile '{name}' deleted.")
