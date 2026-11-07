"""Async search command paths with a mocked Telethon client."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telethon.errors import FloodWaitError
from telethon.tl.types import Message, PeerChannel

from tg_assistant.client_factory import ConfigError
from tg_assistant.search_cmd import _hit_from_tl_message, _search_async


def test_hit_from_tl_message_builds_citeable_hit():
    channel = SimpleNamespace(id=1234567890, title="Market", username="market")
    msg = Message(
        id=9,
        peer_id=PeerChannel(channel_id=1234567890),
        date=None,
        message="hello phone",
    )
    hit = _hit_from_tl_message(msg, chats={1234567890: channel}, users={})
    assert hit["chat_id"] == -1001234567890
    assert hit["chat_title"] == "Market"
    assert hit["username"] == "market"
    assert hit["message_id"] == 9
    assert hit["text"] == "hello phone"
    assert hit["link"] == "https://t.me/market/9"


@pytest.mark.asyncio
async def test_search_rejects_empty_query(capsys):
    code = await _search_async(query="   ", chats=[], limit=10)
    assert code == 1
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["ok"] is False
    assert payload["error"] == "other"


@pytest.mark.asyncio
async def test_search_config_error(capsys):
    with patch(
        "tg_assistant.search_cmd.build_client",
        side_effect=ConfigError("missing env"),
    ):
        code = await _search_async(query="phone", chats=[], limit=10)
    assert code == 1
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["error"] == "other"
    assert "missing env" in payload["message"]


@pytest.mark.asyncio
async def test_search_not_authorized(capsys):
    client = MagicMock()
    client.connect = AsyncMock()
    client.is_user_authorized = AsyncMock(return_value=False)
    client.is_connected.return_value = True
    client.disconnect = AsyncMock()

    with patch("tg_assistant.search_cmd.build_client", return_value=client):
        code = await _search_async(query="phone", chats=[], limit=10)

    assert code == 1
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["error"] == "not_authorized"
    client.disconnect.assert_awaited()


@pytest.mark.asyncio
async def test_search_flood_wait(capsys):
    client = MagicMock()
    client.connect = AsyncMock()
    client.is_user_authorized = AsyncMock(return_value=True)
    client.is_connected.return_value = True
    client.disconnect = AsyncMock()

    with (
        patch("tg_assistant.search_cmd.build_client", return_value=client),
        patch(
            "tg_assistant.search_cmd._global_search",
            AsyncMock(side_effect=FloodWaitError(request=None, capture=12)),
        ),
    ):
        code = await _search_async(query="phone", chats=[], limit=5)

    assert code == 1
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["error"] == "flood_wait"
    assert payload["seconds"] == 12


@pytest.mark.asyncio
async def test_scoped_search_success(capsys):
    client = MagicMock()
    client.connect = AsyncMock()
    client.is_user_authorized = AsyncMock(return_value=True)
    client.is_connected.return_value = True
    client.disconnect = AsyncMock()

    hits = [
        {
            "chat_id": -1001,
            "chat_title": "X",
            "username": None,
            "message_id": 1,
            "date": None,
            "text": "iphone",
            "link": None,
        }
    ]

    with (
        patch("tg_assistant.search_cmd.build_client", return_value=client),
        patch(
            "tg_assistant.search_cmd._scoped_search",
            AsyncMock(return_value=hits),
        ) as scoped,
    ):
        code = await _search_async(query="iphone", chats=["-1001"], limit=5)

    assert code == 0
    scoped.assert_awaited_once()
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["ok"] is True
    assert payload["scoped"] is True
    assert payload["count"] == 1
    assert payload["hits"] == hits
