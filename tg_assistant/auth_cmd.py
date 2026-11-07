"""Interactive auth and machine-readable session status."""

from __future__ import annotations

import asyncio
import sys

from telethon.errors import FloodWaitError, RPCError

from tg_assistant.client_factory import (
    SECONDARY_ACCOUNT_WARNING,
    ConfigError,
    SESSION_PATH,
    build_client,
)
from tg_assistant.errors import emit_json, fail, ok_payload


def _mask_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) <= 4:
        return "***"
    return f"+{'*' * (len(digits) - 4)}{digits[-4:]}"


def _identity(me) -> dict:
    return {
        "id": me.id,
        "username": me.username,
        "phone_masked": _mask_phone(getattr(me, "phone", None)),
        "first_name": me.first_name,
    }


async def _auth_async() -> int:
    print(SECONDARY_ACCOUNT_WARNING, file=sys.stderr)
    print(f"Session file: {SESSION_PATH}.session", file=sys.stderr)
    try:
        client = build_client()
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1

    try:
        await client.start()
        me = await client.get_me()
        if me is None:
            print("Login failed: no user identity returned.", file=sys.stderr)
            return 1
        ident = _identity(me)
        print("Authorized secondary session.", file=sys.stderr)
        print(f"  id: {ident['id']}", file=sys.stderr)
        print(f"  username: {ident['username'] or '(none)'}", file=sys.stderr)
        print(f"  phone: {ident['phone_masked'] or '(none)'}", file=sys.stderr)
        print(f"  name: {ident['first_name'] or ''}", file=sys.stderr)
        return 0
    except FloodWaitError as exc:
        print(
            f"FloodWait: wait {exc.seconds}s before retrying. Not auto-retrying.",
            file=sys.stderr,
        )
        return 1
    except RPCError as exc:
        print(f"Telegram error: {exc}", file=sys.stderr)
        return 1
    finally:
        if client.is_connected():
            await client.disconnect()


async def _status_async() -> int:
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
                session=str(SESSION_PATH) + ".session",
            )
        me = await client.get_me()
        emit_json(
            ok_payload(
                authorized=True,
                session=str(SESSION_PATH) + ".session",
                me=_identity(me),
            )
        )
        return 0
    except FloodWaitError as exc:
        return fail(
            "flood_wait",
            f"Telegram rate limit: wait {exc.seconds}s",
            seconds=exc.seconds,
        )
    except RPCError as exc:
        return fail("other", str(exc))
    finally:
        if client.is_connected():
            await client.disconnect()


def run_auth() -> int:
    return asyncio.run(_auth_async())


def run_status() -> int:
    return asyncio.run(_status_async())
