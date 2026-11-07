# Agent playbook — My Telegram assistant

You help the operator search Telegram from Cursor via the local CLI. Prefer asking here over sending them to the Telegram UI for the same query.

## Rules

- **Secondary account only.** Never suggest logging in the primary personal Telegram account.
- Run CLI from the **repo root**.
- Machine commands (`status`, `dialogs`, `folders`, `search`) → parse **stdout JSON** only.
- On `flood_wait`: report `seconds`, do **not** retry-spam or invent results.
- Do **not** join new chats or bypass rate limits unless the operator explicitly says ok.
- Do not read or commit `.env`, `.data/`, or secrets. `private/` is local operator space (gitignored); use it when they point you there.

## Workflow

1. `python -m tg_assistant status` — if `not_authorized`, ask them to run `python -m tg_assistant auth` in a real terminal.
2. Discover surface: `folders` and/or `dialogs`.
3. Search: `python -m tg_assistant search "…" [--chat …] [--limit N]`.
4. Cite hits with `text`, chat identity, and `link` when present.

## Curated lists

If the operator keeps chat lists under `private/` (e.g. barakholki), prefer those `--chat` ids over blind global search when the task is scoped to that list.

## Scope now

Auth + dialogs/folders + ask-time search. No local index, publish, monitoring, or MCP in this slice. Dev/setup details: [docs/dev.md](docs/dev.md).
