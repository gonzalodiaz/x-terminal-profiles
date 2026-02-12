"""Argument parsing and command dispatch."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

from tp import __version__


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="tp",
        description="Terminal profile manager for multi-client environment isolation",
    )
    parser.add_argument("--version", action="version", version=f"tp {__version__}")

    sub = parser.add_subparsers(dest="command")

    # tp create <name>
    p = sub.add_parser("create", help="Create a new profile interactively")
    p.add_argument("name", help="Profile name")

    # tp list
    sub.add_parser("list", help="List all profiles")

    # tp shell <name>
    p = sub.add_parser("shell", help="Launch isolated shell with profile environment")
    p.add_argument("name", help="Profile name")

    # tp show <name>
    p = sub.add_parser("show", help="Show profile config and environment variables")
    p.add_argument("name", help="Profile name")

    # tp edit <name>
    p = sub.add_parser("edit", help="Open profile.toml in $EDITOR")
    p.add_argument("name", help="Profile name")

    # tp delete <name>
    p = sub.add_parser("delete", help="Delete a profile")
    p.add_argument("name", help="Profile name")

    # tp chrome-profiles
    sub.add_parser("chrome-profiles", help="List available Chrome profiles")

    # tp current
    sub.add_parser("current", help="Show active profile name")

    # tp init-gh <name>
    p = sub.add_parser("init-gh", help="Authenticate GitHub CLI for a profile")
    p.add_argument("name", help="Profile name")

    # tp init-ssh <name>
    p = sub.add_parser("init-ssh", help="Generate SSH key pair for a profile")
    p.add_argument("name", help="Profile name")

    # tp verify <name>
    p = sub.add_parser("verify", help="Validate profile setup")
    p.add_argument("name", help="Profile name")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        raise SystemExit(1)

    if args.command == "create":
        from tp.commands.create import run
        run(args.name)

    elif args.command == "list":
        from tp.commands.list import run
        run()

    elif args.command == "shell":
        from tp.commands.shell import run
        run(args.name)

    elif args.command == "show":
        from tp.commands.show import run
        run(args.name)

    elif args.command == "edit":
        from tp.commands.edit import run
        run(args.name)

    elif args.command == "delete":
        from tp.commands.delete import run
        run(args.name)

    elif args.command == "chrome-profiles":
        from tp.commands.chrome import run
        run()

    elif args.command == "current":
        profile = os.environ.get("TP_PROFILE", "")
        if profile:
            print(profile)
        else:
            print("none")

    elif args.command == "init-gh":
        from tp.commands.init import run_gh
        run_gh(args.name)

    elif args.command == "init-ssh":
        from tp.commands.init import run_ssh
        run_ssh(args.name)

    elif args.command == "verify":
        from tp.commands.verify import run
        run(args.name)
