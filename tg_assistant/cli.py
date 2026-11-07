"""CLI entry: auth | status | dialogs | folders | search."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tg_assistant",
        description=(
            "Local Telegram tools for a SECONDARY user account "
            "(auth, list dialogs/folders, ask-time search)."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("auth", help="Interactive login; persist session under .data/")
    sub.add_parser("status", help="JSON: whether the secondary session is usable")

    dialogs = sub.add_parser("dialogs", help="JSON: list accessible dialogs")
    dialogs.add_argument("--limit", type=int, default=100, help="Max dialogs (default 100)")

    sub.add_parser("folders", help="JSON: list Telegram chat folders and their chats")

    search = sub.add_parser("search", help="JSON: native Telegram search")
    search.add_argument("query", help="Search query")
    search.add_argument(
        "--chat",
        action="append",
        default=[],
        metavar="ID_OR_USERNAME",
        help="Limit search to this chat (repeatable)",
    )
    search.add_argument("--limit", type=int, default=20, help="Max hits (default 20)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "auth":
        from tg_assistant.auth_cmd import run_auth

        return run_auth()
    if args.command == "status":
        from tg_assistant.auth_cmd import run_status

        return run_status()
    if args.command == "dialogs":
        from tg_assistant.dialogs_cmd import run_dialogs

        return run_dialogs(limit=args.limit)
    if args.command == "folders":
        from tg_assistant.folders_cmd import run_folders

        return run_folders()
    if args.command == "search":
        from tg_assistant.search_cmd import run_search

        return run_search(query=args.query, chats=args.chat, limit=args.limit)

    parser.error(f"unknown command: {args.command}")
    return 2
