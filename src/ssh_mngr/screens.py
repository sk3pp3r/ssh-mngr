"""Modal screens — connection form, quick connect, confirm dialog."""

from __future__ import annotations

from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from .models import SSHConnection
from .ssh_import import parse_connection_string


# ---------------------------------------------------------------------------
# Add / Edit Connection
# ---------------------------------------------------------------------------
class ConnectionFormScreen(ModalScreen[Optional[SSHConnection]]):
    """Modal form for creating or editing a connection."""

    CSS = """
    ConnectionFormScreen {
        align: center middle;
    }

    #form-dialog {
        width: 72;
        height: auto;
        max-height: 38;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #form-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        margin-bottom: 1;
    }

    .field-row {
        height: 3;
    }

    .field-label {
        width: 16;
        padding: 1 1 0 0;
        text-align: right;
        color: $text-muted;
    }

    .field-input {
        width: 1fr;
    }

    #btn-row {
        height: 3;
        margin-top: 1;
        align: center middle;
    }

    #btn-row Button {
        margin: 0 2;
    }
    """

    def __init__(
        self,
        connection: SSHConnection | None = None,
        groups: list[str] | None = None,
    ) -> None:
        super().__init__()
        self.connection = connection
        self.existing_groups = groups or ["Default"]
        self.is_edit = connection is not None

    def compose(self) -> ComposeResult:
        c = self.connection
        title = "✏️  Edit Connection" if self.is_edit else "➕  New Connection"

        with Vertical(id="form-dialog"):
            yield Label(title, id="form-title")

            with Horizontal(classes="field-row"):
                yield Label("Name:", classes="field-label")
                yield Input(
                    value=c.name if c else "",
                    placeholder="My Server",
                    id="f-name",
                    classes="field-input",
                )
            with Horizontal(classes="field-row"):
                yield Label("Host:", classes="field-label")
                yield Input(
                    value=c.host if c else "",
                    placeholder="192.168.1.100 or server.example.com",
                    id="f-host",
                    classes="field-input",
                )
            with Horizontal(classes="field-row"):
                yield Label("Port:", classes="field-label")
                yield Input(
                    value=str(c.port) if c else "22",
                    placeholder="22",
                    id="f-port",
                    classes="field-input",
                )
            with Horizontal(classes="field-row"):
                yield Label("Username:", classes="field-label")
                yield Input(
                    value=c.username if c else "",
                    placeholder="root",
                    id="f-user",
                    classes="field-input",
                )
            with Horizontal(classes="field-row"):
                yield Label("Identity File:", classes="field-label")
                yield Input(
                    value=c.identity_file if c else "",
                    placeholder="~/.ssh/id_rsa or /path/to/key.pem",
                    id="f-key",
                    classes="field-input",
                )
            with Horizontal(classes="field-row"):
                yield Label("Group:", classes="field-label")
                yield Input(
                    value=c.group if c else "Default",
                    placeholder="Default",
                    id="f-group",
                    classes="field-input",
                )
            with Horizontal(classes="field-row"):
                yield Label("Description:", classes="field-label")
                yield Input(
                    value=c.description if c else "",
                    placeholder="Optional notes…",
                    id="f-desc",
                    classes="field-input",
                )

            with Horizontal(id="btn-row"):
                yield Button("Save", variant="primary", id="btn-save")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#f-name").focus()

    # -- handlers ----------------------------------------------------------

    @on(Button.Pressed, "#btn-save")
    def _save(self) -> None:
        name = self.query_one("#f-name", Input).value.strip()
        host = self.query_one("#f-host", Input).value.strip()

        if not name or not host:
            self.notify("Name and Host are required!", severity="error")
            return

        try:
            port = int(self.query_one("#f-port", Input).value.strip() or "22")
        except ValueError:
            port = 22

        username = self.query_one("#f-user", Input).value.strip()
        identity = self.query_one("#f-key", Input).value.strip()
        group = self.query_one("#f-group", Input).value.strip() or "Default"
        desc = self.query_one("#f-desc", Input).value.strip()

        if self.is_edit:
            conn = self.connection
            conn.name = name
            conn.host = host
            conn.port = port
            conn.username = username
            conn.identity_file = identity
            conn.group = group
            conn.description = desc
            self.dismiss(conn)
        else:
            self.dismiss(
                SSHConnection(
                    name=name,
                    host=host,
                    port=port,
                    username=username,
                    identity_file=identity,
                    group=group,
                    description=desc,
                )
            )

    @on(Button.Pressed, "#btn-cancel")
    def _cancel(self) -> None:
        self.dismiss(None)

    def key_escape(self) -> None:
        self.dismiss(None)


# ---------------------------------------------------------------------------
# Quick Connect (ad-hoc)
# ---------------------------------------------------------------------------
class QuickConnectScreen(ModalScreen[Optional[SSHConnection]]):
    """Fast ad-hoc SSH connection dialog."""

    CSS = """
    QuickConnectScreen {
        align: center middle;
    }

    #quick-dialog {
        width: 65;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #quick-title {
        text-align: center;
        text-style: bold;
        width: 100%;
    }

    #quick-hint {
        text-align: center;
        color: $text-disabled;
        margin-bottom: 1;
    }

    .field-row { height: 3; }
    .field-label { width: 16; padding: 1 1 0 0; text-align: right; color: $text-muted; }
    .field-input { width: 1fr; }

    #quick-btns {
        height: 3;
        margin-top: 1;
        align: center middle;
    }

    #quick-btns Button { margin: 0 2; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="quick-dialog"):
            yield Label("⚡  Quick Connect", id="quick-title")
            yield Label("Format: [user@]host[:port]", id="quick-hint")

            with Horizontal(classes="field-row"):
                yield Label("Connect to:", classes="field-label")
                yield Input(
                    placeholder="user@host:port",
                    id="q-target",
                    classes="field-input",
                )
            with Horizontal(classes="field-row"):
                yield Label("Identity File:", classes="field-label")
                yield Input(
                    placeholder="(optional) ~/.ssh/key.pem",
                    id="q-key",
                    classes="field-input",
                )

            with Horizontal(id="quick-btns"):
                yield Button("Connect", variant="success", id="btn-go")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#q-target").focus()

    @on(Button.Pressed, "#btn-go")
    def _go(self) -> None:
        self._do_connect()

    @on(Input.Submitted, "#q-target")
    def _submit(self) -> None:
        self._do_connect()

    def _do_connect(self) -> None:
        raw = self.query_one("#q-target", Input).value.strip()
        if not raw:
            self.notify("Enter a host!", severity="error")
            return

        parsed = parse_connection_string(raw)
        key = self.query_one("#q-key", Input).value.strip()

        self.dismiss(
            SSHConnection(
                name=f"quick:{raw}",
                host=parsed["host"],
                port=parsed["port"],
                username=parsed["username"],
                identity_file=key,
                group="_quick_",
            )
        )

    @on(Button.Pressed, "#btn-cancel")
    def _cancel(self) -> None:
        self.dismiss(None)

    def key_escape(self) -> None:
        self.dismiss(None)


# ---------------------------------------------------------------------------
# Confirm dialog
# ---------------------------------------------------------------------------
class ConfirmScreen(ModalScreen[bool]):
    """Yes / No confirmation."""

    CSS = """
    ConfirmScreen {
        align: center middle;
    }

    #confirm-dialog {
        width: 50;
        height: auto;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
    }

    #confirm-msg {
        text-align: center;
        padding: 1;
    }

    #confirm-btns {
        height: 3;
        margin-top: 1;
        align: center middle;
    }

    #confirm-btns Button { margin: 0 2; }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Label(self.message, id="confirm-msg")
            with Horizontal(id="confirm-btns"):
                yield Button("Yes", variant="warning", id="btn-yes")
                yield Button("No", variant="default", id="btn-no")

    @on(Button.Pressed, "#btn-yes")
    def _yes(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#btn-no")
    def _no(self) -> None:
        self.dismiss(False)

    def key_escape(self) -> None:
        self.dismiss(False)


# ---------------------------------------------------------------------------
# About / Help
# ---------------------------------------------------------------------------
class AboutScreen(ModalScreen[None]):
    """About & help screen."""

    CSS = """
    AboutScreen {
        align: center middle;
    }

    #about-dialog {
        width: 64;
        height: auto;
        max-height: 36;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #about-content {
        padding: 1 2;
    }

    #about-close {
        height: 3;
        margin-top: 1;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        from . import __version__

        about_text = (
            "[bold cyan]"
            " ███████ ███████ ██   ██\n"
            " ██      ██      ██   ██\n"
            " ███████ ███████ ███████  ─── Manager\n"
            "      ██      ██ ██   ██\n"
            " ███████ ███████ ██   ██\n"
            "[/]\n"
            f"[bold]Version[/]        {__version__}\n"
            "[bold]Author[/]         Haim Cohen (@sk3pp3r)\n"
            "[bold]License[/]        MIT\n"
            "\n"
            "[bold]Repository[/]     [cyan]github.com/sk3pp3r/ssh-mngr[/cyan]\n"
            "[bold]PyPI[/]           [cyan]pypi.org/project/ssh-mngr[/cyan]\n"
            "[bold]Website[/]        [cyan]sk3pp3r.github.io/ssh-mngr[/cyan]\n"
            "\n"
            "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n"
            "\n"
            "[bold]Keyboard Shortcuts[/]\n"
            "\n"
            "  [cyan]a[/]       Add new connection\n"
            "  [cyan]e[/]       Edit selected connection\n"
            "  [cyan]d[/]       Delete selected connection\n"
            "  [cyan]f[/]       Quick connect (ad-hoc)\n"
            "  [cyan]Enter[/]   Connect to selected server\n"
            "  [cyan]i[/]       Import from ~/.ssh/config\n"
            "  [cyan]s[/]       Focus search bar\n"
            "  [cyan]?[/]       This help screen\n"
            "  [cyan]q[/]       Quit\n"
            "\n"
            "[dim]Config  ~/.config/ssh-mngr/connections.json[/]\n"
            "\n"
            "[dim]Built with Textual + Rich  •  Python 3.9+[/]"
        )

        with Vertical(id="about-dialog"):
            yield Label(about_text, id="about-content")
            with Horizontal(id="about-close"):
                yield Button("Close", variant="primary", id="btn-close")

    @on(Button.Pressed, "#btn-close")
    def _close(self) -> None:
        self.dismiss(None)

    def key_escape(self) -> None:
        self.dismiss(None)

    def key_question_mark(self) -> None:
        self.dismiss(None)


# ---------------------------------------------------------------------------
# Active Sessions (tmux panes)
# ---------------------------------------------------------------------------
class SessionsScreen(ModalScreen[Optional[str]]):
    """Show active SSH sessions (tmux panes) and allow switching/killing."""

    CSS = """
    SessionsScreen {
        align: center middle;
    }

    #sessions-dialog {
        width: 70;
        height: auto;
        max-height: 30;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #sessions-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        margin-bottom: 1;
    }

    #sessions-list {
        height: auto;
        max-height: 18;
        padding: 0 1;
    }

    .session-row {
        height: 3;
    }

    .session-label {
        width: 1fr;
        padding: 1 1 0 0;
    }

    .session-btn {
        width: auto;
        margin: 0 1;
    }

    #sessions-btns {
        height: 3;
        margin-top: 1;
        align: center middle;
    }

    #sessions-btns Button { margin: 0 1; }
    """

    def __init__(self, sessions: list[dict]) -> None:
        super().__init__()
        self.sessions = sessions

    def compose(self) -> ComposeResult:
        with Vertical(id="sessions-dialog"):
            yield Label("📡  Active SSH Sessions", id="sessions-title")
            with Vertical(id="sessions-list"):
                if not self.sessions:
                    yield Label("[dim]No active sessions[/dim]")
                else:
                    for i, s in enumerate(self.sessions):
                        with Horizontal(classes="session-row"):
                            yield Label(
                                f"[bold]{s['name']}[/bold]  [dim]{s.get('host', '')}[/dim]",
                                classes="session-label",
                            )
                            yield Button(
                                "Focus", variant="primary",
                                id=f"focus-{i}", classes="session-btn",
                            )
                            yield Button(
                                "Kill", variant="error",
                                id=f"kill-{i}", classes="session-btn",
                            )
            with Horizontal(id="sessions-btns"):
                yield Button("Broadcast…", variant="warning", id="btn-broadcast")
                yield Button("Close", variant="default", id="btn-close")

    @on(Button.Pressed)
    def _on_button(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id.startswith("focus-"):
            idx = int(btn_id.split("-")[1])
            self.dismiss(f"focus:{self.sessions[idx]['pane_id']}")
        elif btn_id.startswith("kill-"):
            idx = int(btn_id.split("-")[1])
            self.dismiss(f"kill:{self.sessions[idx]['pane_id']}")
        elif btn_id == "btn-broadcast":
            self.dismiss("broadcast")
        elif btn_id == "btn-close":
            self.dismiss(None)

    def key_escape(self) -> None:
        self.dismiss(None)


# ---------------------------------------------------------------------------
# Broadcast command
# ---------------------------------------------------------------------------
class BroadcastScreen(ModalScreen[Optional[str]]):
    """Send a command to all active SSH sessions."""

    CSS = """
    BroadcastScreen {
        align: center middle;
    }

    #broadcast-dialog {
        width: 60;
        height: auto;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
    }

    #broadcast-title {
        text-align: center;
        text-style: bold;
        width: 100%;
    }

    #broadcast-hint {
        text-align: center;
        color: $text-disabled;
        margin-bottom: 1;
    }

    #broadcast-input {
        margin: 1 0;
    }

    #broadcast-btns {
        height: 3;
        margin-top: 1;
        align: center middle;
    }

    #broadcast-btns Button { margin: 0 2; }
    """

    def __init__(self, session_count: int) -> None:
        super().__init__()
        self.session_count = session_count

    def compose(self) -> ComposeResult:
        with Vertical(id="broadcast-dialog"):
            yield Label("📢  Broadcast Command", id="broadcast-title")
            yield Label(
                f"Send to {self.session_count} active session(s)",
                id="broadcast-hint",
            )
            yield Input(
                placeholder="Type command to send to all sessions…",
                id="broadcast-input",
            )
            with Horizontal(id="broadcast-btns"):
                yield Button("Send", variant="warning", id="btn-send")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#broadcast-input").focus()

    @on(Button.Pressed, "#btn-send")
    def _send(self) -> None:
        self._do_send()

    @on(Input.Submitted, "#broadcast-input")
    def _submit(self) -> None:
        self._do_send()

    def _do_send(self) -> None:
        cmd = self.query_one("#broadcast-input", Input).value.strip()
        if cmd:
            self.dismiss(cmd)
        else:
            self.notify("Enter a command!", severity="error")

    @on(Button.Pressed, "#btn-cancel")
    def _cancel(self) -> None:
        self.dismiss(None)

    def key_escape(self) -> None:
        self.dismiss(None)
