# My Telegram assistant

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Telethon](https://img.shields.io/badge/Telethon-1.45-26A5E4?logo=telegram&logoColor=white)](https://docs.telethon.dev/)
[![Telegram](https://img.shields.io/badge/Telegram-MTProto-26A5E4?logo=telegram&logoColor=white)](https://core.telegram.org/)

Local Telegram helper.

- Secondary user account (MTProto / Telethon)
- Ask-time search across joined dialogs
- Dialog and folder listing
- Citeable hits: text, chat, link

## Not in this slice

- Local message index
- Auto-join
- Publishing
- Monitoring
- MCP

## Safety

- Do not authenticate a primary personal account
- Session path: `.data/secondary.session`

## Docs

- Setup / CLI: [docs/dev.md](docs/dev.md)
- Agent playbook: [AGENTS.md](AGENTS.md)
