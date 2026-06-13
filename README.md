# Bombus Discord Bot

Minimal Discord bot that uses local `dronefly-discord` and `dronefly-core` checkouts.

## Setup

This project uses `uv` for dependency management.

1. Install dependencies and lock them with prerelease support:

```bash
cd /home/synrg/work/bombus
uv lock --prerelease=allow
uv install
```

2. Make sure the local packages are available:

- `dronefly-discord` checkout at `/home/synrg/work/dronefly-discord`
- `dronefly-core` checkout at `/home/synrg/work/dronefly-core`

These are referenced in `pyproject.toml` with local file URLs.

## Running

```bash
export BOMBUS_BOT_TOKEN="your-discord-bot-token"
python bot.py
```

## Notes

- The bot currently depends on local package installs from the checkouts above.
- If you update either local checkout, rerun `uv lock --prerelease=allow` and `uv install`.
