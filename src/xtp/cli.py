"""Argument parsing and command dispatch."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

from xtp import __version__


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="xtp",
        description="Terminal profile manager for multi-client environment isolation",
    )
    parser.add_argument("--version", action="version", version=f"xtp {__version__}")

    sub = parser.add_subparsers(dest="command")

    # xtp create <name>
    p = sub.add_parser("create", help="Create a new profile interactively")
    p.add_argument("name", help="Profile name")

    # xtp list
    sub.add_parser("list", help="List all profiles")

    # xtp shell <name>
    p = sub.add_parser("shell", help="Launch isolated shell with profile environment")
    p.add_argument("name", help="Profile name")

    # xtp show [name]
    p = sub.add_parser("show", help="Show profile config and environment variables")
    p.add_argument("name", nargs="?", help="Profile name (defaults to active profile)")

    # xtp edit <name>
    p = sub.add_parser("edit", help="Open profile.toml in $EDITOR")
    p.add_argument("name", help="Profile name")

    # xtp delete <name>
    p = sub.add_parser("delete", help="Delete a profile")
    p.add_argument("name", help="Profile name")

    # xtp chrome-profiles
    sub.add_parser("chrome-profiles", help="List available Chrome profiles")

    # xtp current
    sub.add_parser("current", help="Show active profile name")

    # xtp init-gh <name>
    p = sub.add_parser("init-gh", help="Authenticate GitHub CLI for a profile")
    p.add_argument("name", help="Profile name")

    # xtp init-ssh <name>
    p = sub.add_parser("init-ssh", help="Generate SSH key pair for a profile")
    p.add_argument("name", help="Profile name")

    # xtp verify <name>
    p = sub.add_parser("verify", help="Validate profile setup")
    p.add_argument("name", help="Profile name")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        raise SystemExit(1)

    if args.command == "create":
        from xtp.commands.create import run
        run(args.name)

    elif args.command == "list":
        from xtp.commands.list import run
        run()

    elif args.command == "shell":
        from xtp.commands.shell import run
        run(args.name)

    elif args.command == "show":
        name = args.name or os.environ.get("XTP_PROFILE")
        if not name:
            print("Error: no profile name given and not inside an xtp shell.", file=sys.stderr)
            print("Usage: xtp show <name>  or run from inside an xtp shell.", file=sys.stderr)
            raise SystemExit(1)
        from xtp.commands.show import run
        run(name)

    elif args.command == "edit":
        from xtp.commands.edit import run
        run(args.name)

    elif args.command == "delete":
        from xtp.commands.delete import run
        run(args.name)

    elif args.command == "chrome-profiles":
        from xtp.commands.chrome import run
        run()

    elif args.command == "current":
        profile = os.environ.get("XTP_PROFILE", "")
        if profile:
            print(profile)
        else:
            print("none")

    elif args.command == "init-gh":
        from xtp.commands.init import run_gh
        run_gh(args.name)

    elif args.command == "init-ssh":
        from xtp.commands.init import run_ssh
        run_ssh(args.name)

    elif args.command == "verify":
        from xtp.commands.verify import run
        run(args.name)
