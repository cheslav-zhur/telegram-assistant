"""Build t.me deep links for citeable search hits."""

from __future__ import annotations

from typing import Any


def message_link(
    *,
    message_id: int,
    chat_id: int,
    username: str | None = None,
) -> str | None:
    """Return a t.me link when Telegram allows opening the message by URL."""
    if username:
        return f"https://t.me/{username}/{message_id}"

    # Private/supergroup/channel: https://t.me/c/<internal_id>/<msg_id>
    # Telethon dialog ids for channels/supergroups look like -100xxxxxxxxxx.
    s = str(chat_id)
    if s.startswith("-100"):
        internal = s[4:]
        if internal.isdigit():
            return f"https://t.me/c/{internal}/{message_id}"

    return None


def excerpt(text: str | None, *, max_len: int = 500) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def chat_username(entity: Any) -> str | None:
    username = getattr(entity, "username", None)
    if username:
        return str(username)
    return None
