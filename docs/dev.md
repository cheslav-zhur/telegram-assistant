# Development

## Environment

- Python 3.12 (devcontainer: `mcr.microsoft.com/devcontainers/python:3.12-bookworm`)
- Deps: `requirements.txt` (`telethon`, `python-dotenv`)
- Dev/test: `requirements-dev.txt` (`pytest`, `pytest-asyncio`)
- Secrets: `.env` (gitignored). Session: `.data/secondary.session` (gitignored)
- Local operator notes / curated lists: `private/` (gitignored)

## Setup

```bash
pip install -r requirements.txt   # only after explicit ok / go ahead
pip install -r requirements-dev.txt   # tests; after ok / go ahead
cp .env.example .env              # TELEGRAM_API_ID / TELEGRAM_API_HASH from my.telegram.org
python -m tg_assistant auth       # interactive terminal; secondary account only
python -m tg_assistant status
```

`postCreateCommand` in `.devcontainer/devcontainer.json` runs `pip install -r requirements.txt` on container create.

## Tests

Unit/async tests mock Telethon — no live Telegram, no `.env` / session reads.

```bash
python -m pytest
```

CI: [`.github/workflows/test.yml`](../.github/workflows/test.yml) runs the same on push/PR to `main` (Python 3.12, `requirements-dev.txt`).

## Commands

```bash
python -m tg_assistant status
python -m tg_assistant dialogs [--limit N]
python -m tg_assistant folders
python -m tg_assistant search "query" [--chat ID_OR_USERNAME ...] [--limit N]
```

| Command | stdout |
|---|---|
| `auth` | human text; persists `.data/secondary.session` |
| `status` | JSON identity / authorization |
| `dialogs` | JSON dialog list |
| `folders` | JSON chat folders + resolved chats |
| `search` | JSON hits: text, chat, link |

Machine commands print **JSON only** on stdout. Errors:

```json
{"ok": false, "error": "flood_wait|not_authorized|access|other", "message": "…", "seconds": null}
```

`flood_sleep_threshold = 0` — FloodWait is reported, never auto-retried.

## Package layout

```
tg_assistant/
  cli.py              # argparse entry
  client_factory.py   # .env + TelegramClient
  auth_cmd.py         # auth + status
  dialogs_cmd.py      # iter_dialogs
  folders_cmd.py      # GetDialogFilters
  search_cmd.py       # scoped / SearchGlobalRequest
  links.py            # t.me deep links
  errors.py           # JSON error envelope
```

## Product plan

[plans/2026-11-07-0915-feat-telegram-auth-search-mvp-plan.md](plans/2026-11-07-0915-feat-telegram-auth-search-mvp-plan.md)
