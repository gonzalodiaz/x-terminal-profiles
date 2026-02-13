"""Show profile details and environment variables."""

from __future__ import annotations

from xtp import config


def run(name: str) -> None:
    try:
        cfg = config.load_profile(name)
    except FileNotFoundError:
        print(f"Error: Profile '{name}' not found.")
        raise SystemExit(1)

    desc = cfg.get("profile", {}).get("description", "")
    print(f"Profile: {name}")
    if desc:
        print(f"Description: {desc}")
    print(f"Config: {config.profile_toml(name)}")
    print()

    # Show config sections
    for section in ("git", "chrome", "aws", "npm"):
        if section in cfg and cfg[section]:
            print(f"[{section}]")
            for key, value in cfg[section].items():
                print(f"  {key} = {value}")
            print()

    if "env" in cfg and cfg["env"]:
        print("[env]")
        for key, value in cfg["env"].items():
            print(f"  {key} = {value}")
        print()

    # Show environment variables that would be set
    env = config.build_env(name)
    print("Environment variables:")
    for key in sorted(env):
        print(f"  {key}={env[key]}")
