"""Configuration management — load/save connections as JSON."""

from __future__ import annotations

import json
from pathlib import Path

from .models import SSHConnection

CONFIG_DIR = Path.home() / ".config" / "ssh-mngr"
CONNECTIONS_FILE = CONFIG_DIR / "connections.json"


class Config:
    """Manages SSH connection storage."""

    def __init__(self) -> None:
        self.connections: list[SSHConnection] = []
        self._ensure_dir()
        self.load()

    def _ensure_dir(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        if CONNECTIONS_FILE.exists():
            try:
                data = json.loads(CONNECTIONS_FILE.read_text())
                self.connections = [
                    SSHConnection.from_dict(c) for c in data.get("connections", [])
                ]
            except (json.JSONDecodeError, KeyError):
                self.connections = []
        else:
            self.connections = []

    def save(self) -> None:
        data = {
            "version": 1,
            "connections": [c.to_dict() for c in self.connections],
        }
        CONNECTIONS_FILE.write_text(json.dumps(data, indent=2))

    def add(self, conn: SSHConnection) -> SSHConnection:
        self.connections.append(conn)
        self.save()
        return conn

    def remove(self, conn_id: str) -> None:
        self.connections = [c for c in self.connections if c.id != conn_id]
        self.save()

    def update(self, conn: SSHConnection) -> None:
        for i, c in enumerate(self.connections):
            if c.id == conn.id:
                self.connections[i] = conn
                break
        self.save()

    def find(self, conn_id: str) -> SSHConnection | None:
        for c in self.connections:
            if c.id == conn_id:
                return c
        return None

    def groups(self) -> list[str]:
        groups = sorted(set(c.group for c in self.connections))
        return groups if groups else ["Default"]

    def by_group(self, group: str) -> list[SSHConnection]:
        return sorted(
            [c for c in self.connections if c.group == group],
            key=lambda c: c.name.lower(),
        )

    def search(self, query: str) -> list[SSHConnection]:
        q = query.lower()
        return [
            c
            for c in self.connections
            if q in c.name.lower()
            or q in c.host.lower()
            or q in c.username.lower()
            or q in c.group.lower()
            or q in c.description.lower()
        ]
