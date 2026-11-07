"""List Telegram chat folders (dialog filters) on the secondary account."""

from __future__ import annotations

import asyncio
from typing import Any

from telethon import utils
from telethon.errors import FloodWaitError, RPCError
from telethon.tl.functions.messages import GetDialogFiltersRequest
from telethon.tl.types import (
    Channel,
    Chat,
    DialogFilter,
    DialogFilterChatlist,
    DialogFilterDefault,
    User,
)

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


def _filter_title(filt) -> str:
    title = getattr(filt, "title", None)
    if title is None:
        return ""
    if hasattr(title, "text"):
        return str(title.text or "")
    return str(title)


def _folder_type(filt) -> str:
    if isinstance(filt, DialogFilterChatlist):
        return "chatlist"
    if isinstance(filt, DialogFilter):
        return "filter"
    return "unknown"


def _ordered_peers(filt) -> list[Any]:
    """Pinned first, then include — same order Telegram shows in a folder."""
    seen: set[int] = set()
    ordered: list[Any] = []
    for peer in list(getattr(filt, "pinned_peers", None) or []) + list(
        getattr(filt, "include_peers", None) or []
    ):
        peer_id = utils.get_peer_id(peer)
        if peer_id in seen:
            continue
        seen.add(peer_id)
        ordered.append(peer)
    return ordered


async def _chat_from_peer(client, peer) -> dict[str, Any] | None:
    try:
        entity = await client.get_entity(peer)
    except (ValueError, RPCError):
        return None
    return {
        "id": utils.get_peer_id(peer),
        "title": getattr(entity, "title", None) or getattr(entity, "first_name", None) or "",
        "type": _dialog_type(entity),
        "username": chat_username(entity),
    }


async def _folders_async() -> int:
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

        result = await client(GetDialogFiltersRequest())
        folders: list[dict] = []
        for filt in getattr(result, "filters", None) or []:
            if isinstance(filt, DialogFilterDefault):
                continue
            if not isinstance(filt, (DialogFilter, DialogFilterChatlist)):
                continue

            chats: list[dict] = []
            for peer in _ordered_peers(filt):
                chat = await _chat_from_peer(client, peer)
                if chat is not None:
                    chats.append(chat)

            folders.append(
                {
                    "id": filt.id,
                    "title": _filter_title(filt),
                    "type": _folder_type(filt),
                    "emoticon": getattr(filt, "emoticon", None),
                    "chats": chats,
                    "chat_count": len(chats),
                }
            )

        emit_json(ok_payload(folders=folders, count=len(folders)))
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


def run_folders() -> int:
    return asyncio.run(_folders_async())
