"""Initialization commands: init-gh, init-ssh."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from xtp import config


def run_gh(name: str) -> None:
    """Run gh auth login within the profile's isolated GH_CONFIG_DIR."""
    try:
        env_vars = config.build_env(name)
    except FileNotFoundError:
        print(f"Error: Profile '{name}' not found.")
        raise SystemExit(1)

    gh_dir = config.profile_dir(name) / "gh"
    gh_dir.mkdir(parents=True, exist_ok=True)

    full_env = {**os.environ, **env_vars}
    full_env.pop("GITHUB_TOKEN", None)

    print(f"Authenticating GitHub CLI for profile: {name}")
    print(f"GH_CONFIG_DIR={gh_dir}\n")

    result = subprocess.run(
        ["gh", "auth", "login"],
        env=full_env,
    )
    sys.exit(result.returncode)


def run_ssh(name: str) -> None:
    """Generate a new SSH key pair for the profile."""
    try:
        cfg = config.load_profile(name)
    except FileNotFoundError:
        print(f"Error: Profile '{name}' not found.")
        raise SystemExit(1)

    email = cfg.get("git", {}).get("author_email", "")
    default_path = Path.home() / ".ssh" / f"id_ed25519_{name}"

    path_input = input(f"SSH key path [{default_path}]: ").strip()
    key_path = Path(path_input) if path_input else default_path

    if key_path.exists():
        print(f"Error: Key already exists at {key_path}")
        print("Remove it first or choose a different path.")
        raise SystemExit(1)

    comment = email or name
    result = subprocess.run(
        ["ssh-keygen", "-t", "ed25519", "-C", comment, "-f", str(key_path)],
    )

    if result.returncode != 0:
        raise SystemExit(result.returncode)

    # Update profile with the new key path
    cfg.setdefault("git", {})["ssh_key"] = str(key_path)
    config.save_profile(name, cfg)

    pub_key = key_path.with_suffix(".pub").read_text().strip()
    print(f"\nSSH key generated: {key_path}")
    print(f"Profile updated with new key path.")
    print(f"\nPublic key (add to GitHub):\n")
    print(f"  {pub_key}")
