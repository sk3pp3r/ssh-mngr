"""Import SSH connections from ~/.ssh/config."""

from __future__ import annotations

import re
from pathlib import Path

from .models import SSHConnection


def import_ssh_config() -> list[SSHConnection]:
    """Parse ~/.ssh/config and return a list of SSHConnection objects."""
    config_path = Path.home() / ".ssh" / "config"
    if not config_path.exists():
        return []

    connections: list[SSHConnection] = []
    current: dict[str, str] = {}

    for line in config_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        match = re.match(r"(\w+)\s+(.+)", line)
        if not match:
            continue

        key, value = match.group(1).lower(), match.group(2).strip()

        if key == "host":
            if current and "*" not in current.get("host", ""):
                connections.append(_build_connection(current))
            current = {"host": value}
        elif key == "hostname":
            current["hostname"] = value
        elif key == "port":
            current["port"] = value
        elif key == "user":
            current["user"] = value
        elif key == "identityfile":
            current["identityfile"] = str(Path(value).expanduser())

    # Don't forget the last entry
    if current and "*" not in current.get("host", ""):
        connections.append(_build_connection(current))

    return connections


def _build_connection(entry: dict[str, str]) -> SSHConnection:
    host_alias = entry.get("host", "unnamed")
    hostname = entry.get("hostname", host_alias)
    try:
        port = int(entry.get("port", "22"))
    except ValueError:
        port = 22

    return SSHConnection(
        name=host_alias,
        host=hostname,
        port=port,
        username=entry.get("user", ""),
        identity_file=entry.get("identityfile", ""),
        group="Imported",
    )


def parse_connection_string(s: str) -> dict:
    """Parse user@host:port format into components."""
    result: dict = {"username": "", "host": "", "port": 22}
    s = s.strip()
    if not s:
        return result

    if "@" in s:
        result["username"], s = s.split("@", 1)

    if ":" in s:
        host, port_str = s.rsplit(":", 1)
        try:
            result["port"] = int(port_str)
            result["host"] = host
        except ValueError:
            result["host"] = s
    else:
        result["host"] = s

    return result
