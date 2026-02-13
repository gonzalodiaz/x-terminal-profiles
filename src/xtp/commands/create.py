"""Interactive profile creation."""

from __future__ import annotations

import subprocess
from pathlib import Path

from xtp import config
from xtp.commands.chrome import get_chrome_profiles


def run(name: str) -> None:
    if config.profile_toml(name).exists():
        print(f"Error: Profile '{name}' already exists.")
        raise SystemExit(1)

    print(f"Creating profile: {name}\n")

    # 1. Description
    description = input("Description (e.g. 'Acme Corp'): ").strip()

    # 2. Git author name
    default_name = _git_config("user.name") or ""
    prompt = f"Git author name [{default_name}]: " if default_name else "Git author name: "
    author_name = input(prompt).strip() or default_name

    # 3. Git author email
    author_email = input("Git author email: ").strip()
    if not author_email:
        print("Warning: No email provided. Git identity will be incomplete.")

    # 4. SSH key
    ssh_key = _prompt_ssh_key(name)

    # 5. Chrome profile
    chrome_profile = _prompt_chrome_profile()

    # 6. AWS profile (optional)
    aws_profile = input("AWS profile name (blank to skip): ").strip() or None

    # 7. npm isolation
    npm_isolate_input = input("Isolate npm config? [Y/n]: ").strip().lower()
    npm_isolate = npm_isolate_input != "n"

    # Build profile data
    data: dict = {"profile": {}, "git": {}}

    if description:
        data["profile"]["description"] = description

    if author_name:
        data["git"]["author_name"] = author_name
    if author_email:
        data["git"]["author_email"] = author_email
    if ssh_key:
        data["git"]["ssh_key"] = ssh_key

    if chrome_profile:
        data["chrome"] = {"profile_directory": chrome_profile}

    if aws_profile:
        data["aws"] = {"profile": aws_profile}

    if npm_isolate:
        data["npm"] = {"isolate": True}

    # Create directories and write config
    config.ensure_profile_dirs(name)
    config.seed_claude_config(name)
    config.save_profile(name, data)

    # Generate browser script if needed
    if chrome_profile:
        config.generate_browser_script(name)

    # Create empty npmrc if needed
    if npm_isolate:
        npmrc = config.profile_dir(name) / "npmrc"
        if not npmrc.exists():
            npmrc.touch()

    print(f"\nProfile '{name}' created at {config.profile_dir(name)}")
    print(f"\nNext steps:")
    print(f"  xtp init-gh {name}    # authenticate GitHub CLI")
    print(f"  xtp verify {name}     # check everything is set up")
    print(f"  xtp shell {name}      # activate the profile")
    print()
    print("Tip: See the README for iTerm2 tab integration (title + color).")


def _git_config(key: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "config", "--global", key],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() or None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _prompt_ssh_key(profile_name: str) -> str | None:
    ssh_dir = Path.home() / ".ssh"
    keys = sorted(ssh_dir.glob("id_*")) if ssh_dir.is_dir() else []
    # Filter out .pub files
    keys = [k for k in keys if not k.name.endswith(".pub")]

    if keys:
        print("\nAvailable SSH keys:")
        for i, key in enumerate(keys, 1):
            print(f"  {i}. {key}")
        print(f"  {len(keys) + 1}. Skip (no SSH key)")
        print(f"  {len(keys) + 2}. Enter custom path")

        choice = input(f"Select SSH key [1-{len(keys) + 2}]: ").strip()
        try:
            idx = int(choice)
            if 1 <= idx <= len(keys):
                return str(keys[idx - 1])
            if idx == len(keys) + 2:
                return input("SSH key path: ").strip() or None
        except (ValueError, IndexError):
            pass
        return None
    else:
        path = input("SSH key path (blank to skip): ").strip()
        return path or None


def _prompt_chrome_profile() -> str | None:
    profiles = get_chrome_profiles()
    if not profiles:
        print("\nNo Chrome profiles detected.")
        return None

    print("\nAvailable Chrome profiles:")
    for i, (directory, display_name) in enumerate(profiles, 1):
        print(f"  {i}. {display_name} ({directory})")
    print(f"  {len(profiles) + 1}. Skip (no Chrome profile)")

    choice = input(f"Select Chrome profile [1-{len(profiles) + 1}]: ").strip()
    try:
        idx = int(choice)
        if 1 <= idx <= len(profiles):
            return profiles[idx - 1][0]  # return directory name
    except (ValueError, IndexError):
        pass
    return None
