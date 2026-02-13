"""Profile health check."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from xtp import config
from xtp.commands.chrome import get_chrome_profiles

PASS = "\u2713"  # ✓
FAIL = "\u2717"  # ✗
WARN = "!"


def run(name: str) -> None:
    print(f"Verifying profile: {name}\n")

    passed = 0
    failed = 0
    warned = 0

    def check(label: str, ok: bool, detail: str = "", critical: bool = True) -> None:
        nonlocal passed, failed, warned
        if ok:
            passed += 1
            msg = f"  [{PASS}] {label}"
            if detail:
                msg += f" ({detail})"
            print(msg)
        elif critical:
            failed += 1
            msg = f"  [{FAIL}] {label}"
            if detail:
                msg += f" ({detail})"
            print(msg)
        else:
            warned += 1
            msg = f"  [{WARN}] {label}"
            if detail:
                msg += f" ({detail})"
            print(msg)

    # 1. Profile config
    try:
        cfg = config.load_profile(name)
        check("Profile config exists and is valid", True)
    except Exception as e:
        check("Profile config exists and is valid", False, str(e))
        print(f"\n  0 checks passed (config unreadable)")
        raise SystemExit(1)

    pdir = config.profile_dir(name)

    # 2. Claude config dir
    claude_dir = pdir / "claude"
    if claude_dir.is_dir():
        count = sum(1 for _ in claude_dir.rglob("*") if _.is_file())
        check("Claude Code config dir exists", True, f"{count} files")
    else:
        check("Claude Code config dir exists", False, "directory missing")

    # 3. Git identity
    git = cfg.get("git", {})
    git_name = git.get("author_name", "")
    git_email = git.get("author_email", "")
    if git_name and git_email:
        check("Git identity", True, f"{git_name} <{git_email}>")
    else:
        check("Git identity", False, "author_name or author_email missing")

    # 4. SSH key
    ssh_key = git.get("ssh_key", "")
    if ssh_key:
        key_path = Path(ssh_key).expanduser()
        check("SSH key exists", key_path.is_file(), str(key_path))
    else:
        check("SSH key configured", False, "no ssh_key in config")

    # 5. SSH GitHub connectivity
    if ssh_key and Path(ssh_key).expanduser().is_file():
        key_path = str(Path(ssh_key).expanduser())
        try:
            result = subprocess.run(
                ["ssh", "-T", "-i", key_path, "-o", "IdentitiesOnly=yes",
                 "-o", "StrictHostKeyChecking=accept-new",
                 "git@github.com"],
                capture_output=True, text=True, timeout=10,
            )
            # ssh -T git@github.com exits 1 on success with "successfully authenticated"
            auth_ok = "successfully authenticated" in result.stderr
            check("SSH connects to GitHub", auth_ok,
                  "authenticated" if auth_ok else result.stderr.strip()[:80],
                  critical=False)
        except subprocess.TimeoutExpired:
            check("SSH connects to GitHub", False, "timeout", critical=False)
    else:
        check("SSH connects to GitHub", False, "skipped (no key)", critical=False)

    # 6. GH CLI config dir
    gh_dir = pdir / "gh"
    check("GitHub CLI config dir exists", gh_dir.is_dir())

    # 7. GH CLI auth
    if gh_dir.is_dir():
        try:
            gh_env = {**os.environ, "GH_CONFIG_DIR": str(gh_dir)}
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True, text=True, timeout=10, env=gh_env,
            )
            auth_ok = result.returncode == 0
            check("GitHub CLI authenticated", auth_ok,
                  "logged in" if auth_ok else "not authenticated",
                  critical=False)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            check("GitHub CLI authenticated", False, "gh not found or timeout", critical=False)
    else:
        check("GitHub CLI authenticated", False, "no gh config dir", critical=False)

    # 8. Chrome profile
    chrome = cfg.get("chrome", {})
    chrome_dir = chrome.get("profile_directory", "")
    if chrome_dir:
        profiles = get_chrome_profiles()
        profile_dirs = {d for d, _ in profiles}
        display = dict(profiles).get(chrome_dir, chrome_dir)
        check(f'Chrome profile "{chrome_dir}" exists', chrome_dir in profile_dirs, display)
    else:
        check("Chrome profile configured", False, "no chrome section in config")

    # 9. Browser wrapper
    browser_script = pdir / "browser.sh"
    if chrome_dir:
        ok = browser_script.is_file() and os.access(browser_script, os.X_OK)
        check("Browser wrapper script exists and is executable", ok)
    else:
        check("Browser wrapper script", False, "skipped (no chrome config)", critical=False)

    # 10. AWS config
    aws = cfg.get("aws", {})
    if aws.get("profile"):
        aws_dir = pdir / "aws"
        check("AWS config dir exists", aws_dir.is_dir())
    else:
        check("AWS config", True, "not configured, skipped")

    # 11. npm config
    npm = cfg.get("npm", {})
    if npm.get("isolate"):
        npmrc = pdir / "npmrc"
        check("npm config exists", npmrc.is_file())
    else:
        check("npm config", True, "not configured, skipped")

    # Summary
    total = passed + failed + warned
    print(f"  {'─' * 35}")
    summary = f"  {passed}/{total} checks passed"
    if warned:
        summary += f", {warned} warnings"
    if failed == 0:
        summary += f" {PASS}"
    else:
        summary += f" ({failed} failed)"
    print(summary)

    if failed > 0:
        raise SystemExit(1)
