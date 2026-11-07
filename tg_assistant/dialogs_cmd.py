"""List dialogs the secondary account already can access."""

from __future__ import annotations

import asyncio

from telethon.errors import FloodWaitError, RPCError
from telethon.tl.types import Channel, Chat, User

from tg_assistant.client_factory import ConfigError, build_client
from tg_assistant.errors import emit_json, fail, ok_payload
from tg_assistant.links import chat_username


def _dialog_type(entity) -> str:
    if isinstance(entity, User):
        return "user"
    if isinstance(entity, Chat):
        return "group"
    if isinstance(entity, Channel):
        if getattr(entity, "megagroup", False):
            return "supergroup"
        if getattr(entity, "broadcast", False):
            return "channel"
        return "channel"
    return "unknown"


async def _dialogs_async(*, limit: int) -> int:
    try:
        client = build_client()
    except ConfigError as exc:
        return fail("other", str(exc))

    try:
        await client.connect()
        if not await client.is_user_authorized():
            return fail(
                "not_authorized",
                "No usable secondary session. Run: python -m tg_assistant auth",
            )

        dialogs: list[dict] = []
        async for dialog in client.iter_dialogs(limit=limit):
            entity = dialog.entity
            dialogs.append(
                {
                    "id": dialog.id,
                    "title": dialog.name,
                    "type": _dialog_type(entity),
                    "username": chat_username(entity),
                }
            )

        emit_json(ok_payload(dialogs=dialogs, count=len(dialogs)))
        return 0
    except FloodWaitError as exc:
        return fail(
            "flood_wait",
            f"Telegram rate limit: wait {exc.seconds}s",
            seconds=exc.seconds,
        )
    except RPCError as exc:
        return fail("access" if "ACCESS" in type(exc).__name__.upper() else "other", str(exc))
    finally:
        if client.is_connected():
            await client.disconnect()


def run_dialogs(*, limit: int) -> int:
    return asyncio.run(_dialogs_async(limit=limit))
