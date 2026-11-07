# Development

Local setup and CLI details for this repo.

## Environment

- Python 3.12 (devcontainer image: `mcr.microsoft.com/devcontainers/python:3.12-bookworm`)
- Dependencies pinned in `requirements.txt` (`telethon`, `python-dotenv`)
- Secrets: `.env` (gitignored). Session: `.data/secondary.session` (gitignored)

## Install

From the repo root (after explicit approval to install packages):

```bash
pip install -r requirements.txt
```

`postCreateCommand` in `.devcontainer/devcontainer.json` runs the same install when the container is created.

## Config

```bash
cp .env.example .env
# Fill TELEGRAM_API_ID and TELEGRAM_API_HASH from https://my.telegram.org
# Use a SECONDARY Telegram account only.
```

## First login

Interactive — run in a real terminal (phone code / 2FA prompts):

```bash
python -m tg_assistant auth
```

Then:

```bash
python -m tg_assistant status
```

## Package layout

```
tg_assistant/
  cli.py              # argparse entry
  client_factory.py   # .env + TelegramClient, flood_sleep_threshold=0
  auth_cmd.py         # auth + status
  dialogs_cmd.py      # iter_dialogs → JSON
  folders_cmd.py      # GetDialogFilters → JSON folders + chats
  search_cmd.py       # scoped iter_messages / SearchGlobalRequest → JSON
  links.py            # t.me deep links
  errors.py           # JSON error envelope
```

## CLI contract

| Command | stdout |
|---|---|
| `auth` | human text on stderr/stdout; persists `.data/secondary.session` |
| `status` | JSON identity / authorization |
| `dialogs [--limit N]` | JSON dialog list |
| `folders` | JSON chat folders with resolved chats |
| `search QUERY [--chat …] [--limit N]` | JSON hits with text, chat, link |

Error shape:

```json
{"ok": false, "error": "flood_wait|not_authorized|access|other", "message": "…", "seconds": null}
```

FloodWait is surfaced, never auto-retried (`flood_sleep_threshold = 0`).

## Product plan

Requirements and acceptance examples: [plans/2026-11-07-0915-feat-telegram-auth-search-mvp-plan.md](plans/2026-11-07-0915-feat-telegram-auth-search-mvp-plan.md).
