"""Launch an isolated shell with profile environment variables."""

from __future__ import annotations

import os
import subprocess
import sys

from xtp import config


def run(name: str) -> None:
    # Validate profile exists
    try:
        env = config.build_env(name)
    except FileNotFoundError:
        print(f"Error: Profile '{name}' not found.")
        raise SystemExit(1)

    # Regenerate browser script if Chrome profile is configured
    config.generate_browser_script(name)

    # Build full environment: inherit current env, overlay profile vars
    full_env = {**os.environ, **env}
    # Always clear GITHUB_TOKEN so it can't leak across profiles;
    # gh auth should come from GH_CONFIG_DIR/hosts.yml instead.
    full_env.pop("GITHUB_TOKEN", None)

    print(f"Entering xtp shell: {name}")
    print(f"Type 'exit' to return to your normal shell.\n")

    # Set iTerm2 tab title to the profile name
    os.write(1, f"\033]1;{name}\007".encode())

    result = subprocess.run(
        ["zsh"],
        env=full_env,
    )

    # Reset iTerm2 tab color and title on exit
    os.write(1, b"\033]6;1;bg;*;default\007\033]1;\007")

    sys.exit(result.returncode)
