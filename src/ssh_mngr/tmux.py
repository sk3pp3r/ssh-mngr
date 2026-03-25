"""tmux integration — launch SSH sessions in tmux panes."""

from __future__ import annotations

import os
import shutil
import subprocess


def has_tmux() -> bool:
    """Check if tmux is installed."""
    return shutil.which("tmux") is not None


def inside_tmux() -> bool:
    """Check if we are currently running inside a tmux session."""
    return "TMUX" in os.environ


def tmux_run(*args: str) -> subprocess.CompletedProcess:
    """Run a tmux command and return the result."""
    return subprocess.run(
        ["tmux", *args],
        capture_output=True,
        text=True,
    )


# ── Session management ───────────────────────────────────────────────

def open_ssh_pane(ssh_cmd: list[str], name: str, vertical: bool = False) -> str | None:
    """Open an SSH session in a new tmux pane.

    Returns the pane ID if successful, None otherwise.
    """
    if not inside_tmux():
        return None

    split_flag = "-v" if vertical else "-h"
    cmd_str = " ".join(ssh_cmd)

    result = tmux_run(
        "split-window", split_flag,
        "-d",        # don't switch focus to the new pane
        "-P",        # print pane info
        "-F", "#{pane_id}",
        cmd_str,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def open_ssh_window(ssh_cmd: list[str], name: str) -> str | None:
    """Open an SSH session in a new tmux window.

    Returns the window ID if successful, None otherwise.
    """
    if not inside_tmux():
        return None

    cmd_str = " ".join(ssh_cmd)

    result = tmux_run(
        "new-window",
        "-d",        # don't switch to it
        "-n", name,  # window name
        "-P",        # print info
        "-F", "#{window_id}:#{pane_id}",
        cmd_str,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def select_pane(pane_id: str) -> bool:
    """Switch focus to a tmux pane."""
    result = tmux_run("select-pane", "-t", pane_id)
    return result.returncode == 0


def select_window(target: str) -> bool:
    """Switch focus to a tmux window."""
    result = tmux_run("select-window", "-t", target)
    return result.returncode == 0


def kill_pane(pane_id: str) -> bool:
    """Kill a tmux pane."""
    result = tmux_run("kill-pane", "-t", pane_id)
    return result.returncode == 0


def is_pane_alive(pane_id: str) -> bool:
    """Check if a pane still exists."""
    result = tmux_run(
        "list-panes", "-a",
        "-F", "#{pane_id}",
    )
    if result.returncode != 0:
        return False
    return pane_id in result.stdout.strip().splitlines()


def list_panes() -> list[dict[str, str]]:
    """List all panes in the current session."""
    result = tmux_run(
        "list-panes", "-s",
        "-F", "#{pane_id}\t#{pane_current_command}\t#{window_name}\t#{pane_active}",
    )
    if result.returncode != 0:
        return []

    panes = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("\t")
        if len(parts) >= 4:
            panes.append({
                "pane_id": parts[0],
                "command": parts[1],
                "window": parts[2],
                "active": parts[3] == "1",
            })
    return panes


def send_keys(pane_id: str, keys: str) -> bool:
    """Send keys to a specific pane (for broadcast)."""
    result = tmux_run("send-keys", "-t", pane_id, keys, "Enter")
    return result.returncode == 0


def broadcast_to_panes(pane_ids: list[str], command: str) -> int:
    """Send the same command to multiple panes. Returns success count."""
    count = 0
    for pid in pane_ids:
        if is_pane_alive(pid) and send_keys(pid, command):
            count += 1
    return count


def relaunch_in_tmux(session_name: str = "ssh-mngr") -> None:
    """Re-exec the current app inside a new tmux session.

    This is called when the user runs ssh-mngr outside of tmux
    and tmux is available — we wrap ourselves in tmux automatically.
    """
    # Check if session already exists
    result = tmux_run("has-session", "-t", session_name)
    if result.returncode == 0:
        # Attach to existing session
        os.execvp("tmux", ["tmux", "attach-session", "-t", session_name])
    else:
        # Create new session running our app
        import sys
        app_cmd = " ".join(sys.argv) if sys.argv else "ssh-mngr"
        os.execvp("tmux", [
            "tmux", "new-session", "-s", session_name, app_cmd,
        ])
