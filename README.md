# Bombus Discord Bot

Implements a subset of Dronefly features for large Discord communities for whom
the full feature set of Dronefly is not necessary.

## Setup

This project uses `uv` for dependency management.

1. Install dependencies and lock them with prerelease support:

```bash
git clone https://github.com/dronefly-garden bombus
cd bombus
uv sync --prerelease=allow
```

2. Make sure the local packages are available:

- `dronefly-discord` checkout at `../dronefly-discord`
    - currently on `bombus-menus` branch
- `dronefly-core` checkout at `../dronefly-core`
    - currently on `devel` branch

These are referenced in `pyproject.toml` with absolute local file URLs that need
to be edited to match your actual local paths to them.

## Running

```bash
export BOMBUS_BOT_TOKEN="your-discord-bot-token"
python bot.py
```

## Notes

- The bot currently depends on local package installs from the checkouts above.
- If you update either local checkout, rerun `uv sync --prerelease=allow`.
