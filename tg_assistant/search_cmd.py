"""Ask-time native Telegram search (scoped or global)."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from telethon import utils
from telethon.errors import FloodWaitError, RPCError
from telethon.tl.functions.messages import SearchGlobalRequest
from telethon.tl.types import InputMessagesFilterEmpty, InputPeerEmpty, Message, PeerChannel, PeerChat, PeerUser

from tg_assistant.client_factory import ConfigError, build_client
from tg_assistant.errors import emit_json, fail, ok_payload
from tg_assistant.links import chat_username, excerpt, message_link


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _entity_maps(result) -> tuple[dict[int, Any], dict[int, Any]]:
    chats = {c.id: c for c in (getattr(result, "chats", None) or [])}
    users = {u.id: u for u in (getattr(result, "users", None) or [])}
    return chats, users


def _resolve_peer_entity(peer, chats: dict[int, Any], users: dict[int, Any]):
    if isinstance(peer, PeerChannel):
        return chats.get(peer.channel_id)
    if isinstance(peer, PeerChat):
        return chats.get(peer.chat_id)
    if isinstance(peer, PeerUser):
        return users.get(peer.user_id)
    return None


def _hit_from_tl_message(msg: Message, chats: dict[int, Any], users: dict[int, Any]) -> dict[str, Any]:
    entity = _resolve_peer_entity(msg.peer_id, chats, users)
    title = ""
    username = None
    if entity is not None:
        title = getattr(entity, "title", None) or getattr(entity, "first_name", None) or ""
        username = chat_username(entity)
    chat_id = utils.get_peer_id(msg.peer_id)
    return {
        "chat_id": chat_id,
        "chat_title": title,
        "username": username,
        "message_id": msg.id,
        "date": _iso(msg.date),
        "text": excerpt(getattr(msg, "message", None)),
        "link": message_link(message_id=msg.id, chat_id=chat_id, username=username),
    }


async def _hit_from_message(message) -> dict[str, Any]:
    chat = await message.get_chat()
    title = getattr(chat, "title", None) or getattr(chat, "first_name", None) or ""
    username = chat_username(chat)
    chat_id = message.chat_id if message.chat_id is not None else getattr(chat, "id", 0)
    return {
        "chat_id": chat_id,
        "chat_title": title,
        "username": username,
        "message_id": message.id,
        "date": _iso(message.date),
        "text": excerpt(message.message or message.text),
        "link": message_link(
            message_id=message.id,
            chat_id=chat_id,
            username=username,
        ),
    }


async def _scoped_search(client, *, query: str, chats: list[str], limit: int) -> list[dict]:
    hits: list[dict] = []
    per_chat = max(1, limit // max(1, len(chats)))
    for chat_ref in chats:
        if len(hits) >= limit:
            break
        remaining = limit - len(hits)
        take = min(per_chat, remaining)
        async for message in client.iter_messages(chat_ref, search=query, limit=take):
            hits.append(await _hit_from_message(message))
            if len(hits) >= limit:
                break
    return hits


async def _global_search(client, *, query: str, limit: int) -> list[dict]:
    hits: list[dict] = []
    offset_rate = 0
    offset_peer: Any = InputPeerEmpty()
    offset_id = 0

    while len(hits) < limit:
        batch_limit = min(100, limit - len(hits))
        result = await client(
            SearchGlobalRequest(
                q=query,
                filter=InputMessagesFilterEmpty(),
                min_date=None,
                max_date=None,
                offset_rate=offset_rate,
                offset_peer=offset_peer,
                offset_id=offset_id,
                limit=batch_limit,
            )
        )
        messages = [m for m in (getattr(result, "messages", None) or []) if isinstance(m, Message)]
        if not messages:
            break

        chats, users = _entity_maps(result)
        for msg in messages:
            hits.append(_hit_from_tl_message(msg, chats, users))
            if len(hits) >= limit:
                break

        last = messages[-1]
        next_rate = getattr(result, "next_rate", None)
        if next_rate is None:
            break
        offset_rate = next_rate
        offset_peer = last.peer_id
        offset_id = last.id

    return hits


async def _search_async(*, query: str, chats: list[str], limit: int) -> int:
    if not query.strip():
        return fail("other", "Query must not be empty")

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

        scoped = bool(chats)
        if scoped:
            hits = await _scoped_search(client, query=query, chats=chats, limit=limit)
        else:
            hits = await _global_search(client, query=query, limit=limit)

        emit_json(
            ok_payload(
                query=query,
                scoped=scoped,
                chats=chats or None,
                count=len(hits),
                hits=hits,
            )
        )
        return 0
    except FloodWaitError as exc:
        return fail(
            "flood_wait",
            f"Telegram rate limit: wait {exc.seconds}s",
            seconds=exc.seconds,
        )
    except (ValueError, RPCError) as exc:
        name = type(exc).__name__.upper()
        kind = "access" if "ACCESS" in name or "PEER" in name else "other"
        return fail(kind, str(exc))
    finally:
        if client.is_connected():
            await client.disconnect()


def run_search(*, query: str, chats: list[str], limit: int) -> int:
    return asyncio.run(_search_async(query=query, chats=chats, limit=limit))
