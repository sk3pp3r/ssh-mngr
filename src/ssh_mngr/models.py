"""Data models for SSH connections."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SSHConnection:
    """Represents a saved SSH connection."""

    name: str
    host: str
    port: int = 22
    username: str = ""
    identity_file: str = ""
    group: str = "Default"
    description: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    last_connected: str = ""

    @property
    def display_name(self) -> str:
        parts = []
        if self.username:
            parts.append(f"{self.username}@")
        parts.append(self.host)
        if self.port != 22:
            parts.append(f":{self.port}")
        return f"{self.name}  ({''.join(parts)})"

    def build_command(self) -> list[str]:
        """Build the SSH command as a list of arguments."""
        cmd = ["ssh"]
        if self.port != 22:
            cmd.extend(["-p", str(self.port)])
        if self.identity_file:
            cmd.extend(["-i", os.path.expanduser(self.identity_file)])
        target = f"{self.username}@{self.host}" if self.username else self.host
        cmd.append(target)
        return cmd

    def command_string(self) -> str:
        """Human-readable SSH command string."""
        cmd = ["ssh"]
        if self.port != 22:
            cmd.extend(["-p", str(self.port)])
        if self.identity_file:
            cmd.extend(["-i", self.identity_file])
        target = f"{self.username}@{self.host}" if self.username else self.host
        cmd.append(target)
        return " ".join(cmd)

    def touch(self) -> None:
        """Update last-connected timestamp."""
        self.last_connected = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "identity_file": self.identity_file,
            "group": self.group,
            "description": self.description,
            "last_connected": self.last_connected,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SSHConnection:
        valid = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in valid})
