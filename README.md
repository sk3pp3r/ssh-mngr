# SSH Manager (`ssh-mngr`)

> **A beautiful terminal SSH connection manager — like mRemoteNG / RoyalTSX, but right inside your terminal.**

[![PyPI version](https://img.shields.io/pypi/v/ssh-mngr)](https://pypi.org/project/ssh-mngr/)
[![Python 3.9+](https://img.shields.io/pypi/pyversions/ssh-mngr)](https://pypi.org/project/ssh-mngr/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Built with [Textual](https://textual.textualize.io/) + [Rich](https://rich.readthedocs.io/) — no GUI, no browser, just your terminal.

---

## ✨ Why?

If you SSH into multiple Linux servers daily — some with your user, some with `root`, some with PEM keys — you need a fast way to manage, search, and connect. No more scrolling through bash history or maintaining shell aliases.

**ssh-mngr** gives you a Norton Commander-style TUI with a sidebar of grouped connections, a detail panel, live search, and one-key connect.

---

## 📦 Install

```bash
# Homebrew (macOS)
brew tap sk3pp3r/ssh-mngr https://github.com/sk3pp3r/ssh-mngr
brew install ssh-mngr

# From PyPI
pipx install ssh-mngr

# Or with pip
pip install ssh-mngr
```

### Install from source

```bash
git clone https://github.com/sk3pp3r/ssh-mngr.git
cd ssh-mngr
pip install .
```

### Offline install (air-gapped servers)

```bash
# On a machine with internet — build wheels
pip wheel . -w dist/
pip download -d dist/ .

# Transfer the dist/ folder via sftp/scp
sftp user@offline-host
sftp> put dist/* /tmp/ssh-mngr-wheels/

# On the offline machine
pip install --no-index --find-links=/tmp/ssh-mngr-wheels/ ssh-mngr
```

---

## 🚀 Usage

```bash
ssh-mngr     # launch the TUI
ssm           # short alias — same thing
```

---

## ⌨️ Keyboard Shortcuts

| Key       | Action                                |
|-----------|---------------------------------------|
| `a`       | **Add** new connection                |
| `e`       | **Edit** selected connection          |
| `d`       | **Delete** selected connection        |
| `f`       | **Quick connect** — ad-hoc SSH        |
| `Enter`   | **Connect** to selected server        |
| `i`       | **Import** from `~/.ssh/config`       |
| `s`       | **Search** — focus the filter bar     |
| `q`       | **Quit**                              |

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **Grouped connections** | Organise servers into named folders |
| **PEM / identity-file** | Per-connection key file support |
| **Quick connect** | Ad-hoc `user@host:port` without saving |
| **SSH config import** | One-key import from `~/.ssh/config` |
| **Live search** | Filter connections as you type |
| **Detail panel** | Shows host info, SSH command, last-connected |
| **Last connected** | Tracks when you last used each connection |
| **Cross-platform** | Works on macOS and Linux terminals |

---

## 🏗️ Project Structure

```
src/ssh_mngr/
├── app.py          # Main Textual app — layout, keybindings, SSH launch
├── screens.py      # Modal dialogs (add/edit/quick-connect/confirm)
├── config.py       # JSON config load/save
├── models.py       # SSHConnection dataclass
└── ssh_import.py   # ~/.ssh/config parser
```

---

## ⚙️ Configuration

Connections are stored as JSON at:

```
~/.config/ssh-mngr/connections.json
```

Example:

```json
{
  "version": 1,
  "connections": [
    {
      "id": "a1b2c3d4",
      "name": "Production Web",
      "host": "10.0.1.50",
      "port": 22,
      "username": "deploy",
      "identity_file": "~/.ssh/prod.pem",
      "group": "Production",
      "description": "Main web server",
      "last_connected": "2026-03-25T14:30:00"
    }
  ]
}
```

---

## 🗺️ Roadmap

- [ ] Duplicate connection
- [ ] SSH tunnels / port forwarding
- [ ] Connection tags & multi-group
- [ ] Export / import connections (JSON / YAML)
- [ ] SCP / file transfer shortcut
- [ ] Theme customisation

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
