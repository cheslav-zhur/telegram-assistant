"""Load credentials and build a TelegramClient bound to the secondary session."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient

# Repo root: …/telegram-assistant (parent of tg_assistant/)
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / ".data"
SESSION_PATH = DATA_DIR / "secondary"
ENV_PATH = REPO_ROOT / ".env"

SECONDARY_ACCOUNT_WARNING = (
    "WARNING: Use a SECONDARY Telegram account only. "
    "Do not auth your primary personal account with this tool."
)


class ConfigError(Exception):
    """Missing or invalid local configuration."""


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_api_credentials() -> tuple[int, str]:
    load_dotenv(ENV_PATH)
    raw_id = os.getenv("TELEGRAM_API_ID", "").strip()
    api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
    if not raw_id or not api_hash:
        raise ConfigError(
            f"Set TELEGRAM_API_ID and TELEGRAM_API_HASH in {ENV_PATH} "
            "(copy from .env.example). Create an app at https://my.telegram.org "
            "using a SECONDARY account."
        )
    try:
        api_id = int(raw_id)
    except ValueError as exc:
        raise ConfigError("TELEGRAM_API_ID must be an integer") from exc
    return api_id, api_hash


def build_client() -> TelegramClient:
    """Create a client with flood auto-sleep disabled (surface FloodWait instead)."""
    ensure_data_dir()
    api_id, api_hash = load_api_credentials()
    client = TelegramClient(str(SESSION_PATH), api_id, api_hash)
    client.flood_sleep_threshold = 0
    return client
