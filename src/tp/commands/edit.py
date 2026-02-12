"""Open profile.toml in $EDITOR."""

from __future__ import annotations

import os
import subprocess
import sys

from tp import config


def run(name: str) -> None:
    path = config.profile_toml(name)
    if not path.is_file():
        print(f"Error: Profile '{name}' not found.")
        raise SystemExit(1)

    editor = os.environ.get("EDITOR", "vim")
    result = subprocess.run([editor, str(path)])
    sys.exit(result.returncode)
