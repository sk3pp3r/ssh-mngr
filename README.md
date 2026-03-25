# SSH Manager (`ssh-mngr`)

A beautiful terminal SSH connection manager — like mRemoteNG / RoyalTSX for your terminal.

Built with [Textual](https://textual.textualize.io/) + [Rich](https://rich.readthedocs.io/).

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)

## Install

```bash
# From source
pip install .

# Or with pipx (isolated)
pipx install .

# Development
pip install -e .
```

## Usage

```bash
ssh-mngr     # launch the TUI
ssm           # short alias
```

## Keyboard Shortcuts

| Key     | Action                          |
|---------|---------------------------------|
| `a`     | Add new connection              |
| `e`     | Edit selected connection        |
| `d`     | Delete selected connection      |
| `f`     | Quick connect (ad-hoc)          |
| `Enter` | Connect to selected server      |
| `i`     | Import from `~/.ssh/config`     |
| `s`     | Focus search bar                |
| `q`     | Quit                            |

## Features

- **Grouped connections** — organise servers into folders
- **PEM / identity-file support** — per-connection key files
- **Quick connect** — ad-hoc `user@host:port` without saving
- **SSH config import** — one-key import from `~/.ssh/config`
- **Live search** — filter connections as you type
- **Norton Commander feel** — side panel + detail view
- **Last connected** — tracks when you last used each connection
- **Cross-platform** — macOS & Linux terminals

## Config

Connections are stored in `~/.config/ssh-mngr/connections.json`.

## License

MIT
