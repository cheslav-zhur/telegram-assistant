# telegram-assistant

Local CLI for Cursor: sign in a **secondary** Telegram user account and run ask-time search across dialogs that account already joined (Telethon / MTProto).

## Safety: secondary account only

Do **not** authenticate your primary personal Telegram account. Use a separate account that already belongs to the target groups/channels. The session file is `.data/secondary.session`.

## Quick start

1. Create an app at [my.telegram.org](https://my.telegram.org) with the **secondary** account.
2. Copy `.env.example` → `.env` and set `TELEGRAM_API_ID` / `TELEGRAM_API_HASH`.
3. Install deps and log in once (interactive terminal) — see [docs/dev.md](docs/dev.md).

```bash
python -m tg_assistant status
python -m tg_assistant dialogs
python -m tg_assistant folders
python -m tg_assistant search "query"
python -m tg_assistant search "query" --chat -1001234567890 --limit 20
```

Machine commands (`status`, `dialogs`, `folders`, `search`) print **JSON only** on stdout. On rate limits they return `{"ok":false,"error":"flood_wait","seconds":N}` and a non-zero exit code (no auto-retry).

## For Cursor Agent

1. Run `python -m tg_assistant status`.
2. If `not_authorized`, ask the operator to run `auth` in a real terminal.
3. Use `dialogs` or `folders` to see the searchable surface, then `search "…"` (optionally with `--chat`).

This slice is auth + list dialogs/folders + ask-time search only. No local index, join, publish, or MCP.
