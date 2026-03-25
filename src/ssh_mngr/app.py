"""SSH Manager — Main Textual Application."""

from __future__ import annotations

import subprocess

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, Label, Static, Tree
from textual.widgets.tree import TreeNode

from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .config import Config
from .models import SSHConnection
from .screens import (
    AboutScreen,
    BroadcastScreen,
    ConfirmScreen,
    ConnectionFormScreen,
    QuickConnectScreen,
    SessionsScreen,
)
from .ssh_import import import_ssh_config
from . import tmux as tmux_mgr

# ── Welcome splash ────────────────────────────────────────────────────────

WELCOME_TEMPLATE = """\
[bold cyan]
 ███████ ███████ ██   ██
 ██      ██      ██   ██
 ███████ ███████ ███████  ─── Manager
      ██      ██ ██   ██
 ███████ ███████ ██   ██
[/]
[dim]Terminal SSH Connection Manager  v{version}[/]

[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]

{tmux_status}

[bold]Keyboard Shortcuts[/]

  [cyan]a[/]       Add new connection
  [cyan]e[/]       Edit selected
  [cyan]d[/]       Delete selected
  [cyan]f[/]       Quick connect  (ad-hoc)
  [cyan]i[/]       Import from ~/.ssh/config
  [cyan]Enter[/]   Connect to selected server
  [cyan]t[/]       Active sessions (tmux)
  [cyan]b[/]       Broadcast command to all sessions
  [cyan]s[/]       Focus search bar
  [cyan]?[/]       About / Help
  [cyan]q[/]       Quit

[dim]Config  ~/.config/ssh-mngr/connections.json[/]
"""


def _build_welcome() -> str:
    from . import __version__

    if tmux_mgr.inside_tmux():
        status = "[bold green]● tmux[/]  Sessions open in panes — TUI stays visible"
    elif tmux_mgr.has_tmux():
        status = "[bold yellow]○ tmux[/]  Available — run inside tmux for pane mode"
    else:
        status = "[dim]○ tmux  Not installed — sessions open in full screen[/]"

    return WELCOME_TEMPLATE.format(version=__version__, tmux_status=status)


# ── Detail panel widget ───────────────────────────────────────────────────

class ConnectionDetail(Static):
    """Right-hand panel showing connection info or welcome screen."""

    def show_welcome(self) -> None:
        self.update(_build_welcome())

    def show_connection(self, conn: SSHConnection) -> None:
        tbl = Table(
            show_header=False,
            box=box.SIMPLE,
            padding=(0, 2),
            expand=True,
        )
        tbl.add_column("Key", style="bold cyan", width=16)
        tbl.add_column("Value")

        tbl.add_row("Host", conn.host)
        tbl.add_row("Port", str(conn.port))
        tbl.add_row("Username", conn.username or "[dim]current user[/dim]")
        if conn.identity_file:
            tbl.add_row("Identity File", conn.identity_file)
        tbl.add_row("Group", conn.group)
        if conn.description:
            tbl.add_row("Description", conn.description)
        if conn.last_connected:
            tbl.add_row(
                "Last Connected",
                conn.last_connected[:19].replace("T", " "),
            )
        tbl.add_row("", "")
        tbl.add_row("SSH Command", Text(conn.command_string(), style="green"))

        icon = "🔑" if conn.identity_file else "🖥"
        panel = Panel(
            tbl,
            title=f" {icon}  {conn.name} ",
            title_align="left",
            border_style="cyan",
            padding=(1, 2),
        )
        self.update(panel)


# ── Main app ──────────────────────────────────────────────────────────────

class SSHManagerApp(App):
    """SSH Connection Manager TUI."""

    TITLE = "SSH Manager"
    SUB_TITLE = "Manage your SSH connections"

    CSS = """
    Screen {
        background: $surface;
    }

    #app-grid {
        height: 1fr;
    }

    /* ── Sidebar ── */
    #sidebar {
        width: 42;
        background: $panel;
        border-right: tall $primary;
    }

    #sidebar-title {
        dock: top;
        width: 100%;
        background: $primary;
        color: auto;
        text-align: center;
        text-style: bold;
        height: 1;
    }

    #search-box {
        dock: top;
        border: none;
        background: $boost;
        height: 3;
        margin: 0;
    }

    #conn-tree {
        height: 1fr;
        scrollbar-size: 1 1;
        padding: 0 1;
        background: $panel;
    }

    #conn-tree:focus {
        border: none;
    }

    Tree > .tree--cursor {
        background: $accent;
        color: auto;
        text-style: bold;
    }

    Tree > .tree--highlight-line {
        background: $accent 20%;
    }

    /* ── Main panel ── */
    #main-panel {
        width: 1fr;
        padding: 1 2;
    }

    #detail {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("a", "add_connection", "Add"),
        Binding("e", "edit_connection", "Edit"),
        Binding("d", "delete_connection", "Delete"),
        Binding("f", "quick_connect", "Quick ⚡"),
        Binding("enter", "do_connect", "Connect", show=True),
        Binding("i", "import_config", "Import"),
        Binding("t", "show_sessions", "Sessions"),
        Binding("b", "broadcast", "Broadcast"),
        Binding("s", "search_focus", "Search"),
        Binding("question_mark", "show_about", "About ?"),
    ]

    selected_connection: reactive[SSHConnection | None] = reactive(None)

    def __init__(self) -> None:
        super().__init__()
        self.config_mgr = Config()
        self.active_sessions: list[dict] = []  # tracks tmux pane sessions

    # ── compose ───────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="app-grid"):
            with Vertical(id="sidebar"):
                yield Label(" 🖥  CONNECTIONS ", id="sidebar-title")
                yield Input(placeholder=" 🔍  Search…", id="search-box")
                yield Tree("Servers", id="conn-tree")
            with Vertical(id="main-panel"):
                yield ConnectionDetail(id="detail")
        yield Footer()

    def on_mount(self) -> None:
        self._rebuild_tree()
        tree = self.query_one("#conn-tree", Tree)
        tree.root.expand()
        tree.focus()
        self.query_one("#detail", ConnectionDetail).show_welcome()

    # ── tree helpers ──────────────────────────────────────────────────

    def _rebuild_tree(self, filter_text: str = "") -> None:
        tree = self.query_one("#conn-tree", Tree)
        tree.clear()

        connections = self.config_mgr.connections
        if filter_text:
            connections = self.config_mgr.search(filter_text)

        groups: dict[str, list[SSHConnection]] = {}
        for conn in connections:
            groups.setdefault(conn.group, []).append(conn)

        if not groups:
            tree.root.add_leaf("[dim]No connections — press [bold]a[/bold] to add[/dim]")
            tree.root.expand()
            return

        for gname in sorted(groups):
            cnt = len(groups[gname])
            gnode = tree.root.add(f"📁 {gname} ({cnt})", expand=True)
            gnode.data = {"type": "group", "name": gname}
            for conn in sorted(groups[gname], key=lambda c: c.name.lower()):
                icon = "🔑" if conn.identity_file else "🖥 "
                leaf = gnode.add_leaf(f"{icon} {conn.name}")
                leaf.data = {"type": "connection", "connection": conn}

        tree.root.expand_all()

    def _selected(self) -> SSHConnection | None:
        tree = self.query_one("#conn-tree", Tree)
        node = tree.cursor_node
        if node and node.data and node.data.get("type") == "connection":
            return node.data["connection"]
        return None

    # ── event handlers ────────────────────────────────────────────────

    @on(Tree.NodeHighlighted)
    def _on_highlight(self, event: Tree.NodeHighlighted) -> None:
        detail = self.query_one("#detail", ConnectionDetail)
        node = event.node
        if node.data and node.data.get("type") == "connection":
            conn = node.data["connection"]
            self.selected_connection = conn
            detail.show_connection(conn)
        else:
            self.selected_connection = None
            detail.show_welcome()

    @on(Tree.NodeSelected)
    def _on_select(self, event: Tree.NodeSelected) -> None:
        node = event.node
        if node.data and node.data.get("type") == "connection":
            self._ssh_connect(node.data["connection"])

    @on(Input.Changed, "#search-box")
    def _on_search(self, event: Input.Changed) -> None:
        self._rebuild_tree(event.value)

    # ── actions (key bindings) ────────────────────────────────────────

    def action_add_connection(self) -> None:
        self.push_screen(
            ConnectionFormScreen(groups=self.config_mgr.groups()),
            callback=self._cb_add,
        )

    def action_edit_connection(self) -> None:
        conn = self._selected()
        if not conn:
            self.notify("Select a connection first", severity="warning")
            return
        self.push_screen(
            ConnectionFormScreen(connection=conn, groups=self.config_mgr.groups()),
            callback=self._cb_edit,
        )

    def action_delete_connection(self) -> None:
        conn = self._selected()
        if not conn:
            self.notify("Select a connection first", severity="warning")
            return
        self.push_screen(
            ConfirmScreen(f"Delete [bold]{conn.name}[/bold]?"),
            callback=lambda ok: self._cb_delete(ok, conn),
        )

    def action_quick_connect(self) -> None:
        self.push_screen(QuickConnectScreen(), callback=self._cb_quick)

    def action_do_connect(self) -> None:
        conn = self._selected()
        if conn:
            self._ssh_connect(conn)

    def action_import_config(self) -> None:
        imported = import_ssh_config()
        if not imported:
            self.notify(
                "No entries found in ~/.ssh/config", severity="warning"
            )
            return

        existing = {
            (c.host, c.port, c.username) for c in self.config_mgr.connections
        }
        new = [
            c for c in imported if (c.host, c.port, c.username) not in existing
        ]

        if not new:
            self.notify("All SSH config entries already imported")
            return

        for c in new:
            self.config_mgr.add(c)

        self._rebuild_tree()
        self.notify(f"Imported {len(new)} connection(s)")

    def action_search_focus(self) -> None:
        self.query_one("#search-box", Input).focus()

    def action_show_about(self) -> None:
        self.push_screen(AboutScreen())

    def action_show_sessions(self) -> None:
        self._prune_dead_sessions()
        if not self.active_sessions:
            self.notify("No active sessions", severity="warning")
            return
        self.push_screen(
            SessionsScreen(self.active_sessions),
            callback=self._cb_sessions,
        )

    def action_broadcast(self) -> None:
        self._prune_dead_sessions()
        if not self.active_sessions:
            self.notify("No active sessions to broadcast to", severity="warning")
            return
        self.push_screen(
            BroadcastScreen(len(self.active_sessions)),
            callback=self._cb_broadcast,
        )

    # ── callbacks ─────────────────────────────────────────────────────

    def _cb_add(self, conn: SSHConnection | None) -> None:
        if conn:
            self.config_mgr.add(conn)
            self._rebuild_tree()
            self.notify(f"Added [bold]{conn.name}[/bold]")

    def _cb_edit(self, conn: SSHConnection | None) -> None:
        if conn:
            self.config_mgr.update(conn)
            self._rebuild_tree()
            detail = self.query_one("#detail", ConnectionDetail)
            detail.show_connection(conn)
            self.notify(f"Updated [bold]{conn.name}[/bold]")

    def _cb_delete(self, confirmed: bool, conn: SSHConnection) -> None:
        if confirmed:
            self.config_mgr.remove(conn.id)
            self._rebuild_tree()
            self.query_one("#detail", ConnectionDetail).show_welcome()
            self.notify(f"Deleted {conn.name}")

    def _cb_quick(self, conn: SSHConnection | None) -> None:
        if conn:
            self._ssh_connect(conn)

    def _cb_sessions(self, action: str | None) -> None:
        if not action:
            return
        if action.startswith("focus:"):
            pane_id = action.split(":", 1)[1]
            tmux_mgr.select_pane(pane_id)
            self.notify(f"Switched to pane {pane_id}")
        elif action.startswith("kill:"):
            pane_id = action.split(":", 1)[1]
            tmux_mgr.kill_pane(pane_id)
            self.active_sessions = [
                s for s in self.active_sessions if s["pane_id"] != pane_id
            ]
            self.notify(f"Killed session in pane {pane_id}")
        elif action == "broadcast":
            self.action_broadcast()

    def _cb_broadcast(self, command: str | None) -> None:
        if not command:
            return
        self._prune_dead_sessions()
        pane_ids = [s["pane_id"] for s in self.active_sessions]
        count = tmux_mgr.broadcast_to_panes(pane_ids, command)
        self.notify(f"Sent to {count}/{len(pane_ids)} session(s)")

    # ── session helpers ───────────────────────────────────────────────

    def _prune_dead_sessions(self) -> None:
        """Remove sessions whose tmux pane no longer exists."""
        self.active_sessions = [
            s for s in self.active_sessions
            if tmux_mgr.is_pane_alive(s["pane_id"])
        ]

    # ── SSH ───────────────────────────────────────────────────────────

    def _ssh_connect(self, conn: SSHConnection) -> None:
        # Persist last-connected for saved connections
        if self.config_mgr.find(conn.id):
            conn.touch()
            self.config_mgr.update(conn)

        cmd = conn.build_command()

        if tmux_mgr.inside_tmux():
            # Open SSH in a new tmux pane — TUI stays visible
            pane_id = tmux_mgr.open_ssh_pane(cmd, conn.name)
            if pane_id:
                self.active_sessions.append({
                    "name": conn.name,
                    "host": conn.host,
                    "pane_id": pane_id,
                    "conn_id": conn.id,
                })
                self.notify(
                    f"[green]⚡[/] {conn.name} opened in tmux pane {pane_id}"
                )
            else:
                self.notify("Failed to open tmux pane", severity="error")
        else:
            # Fallback: suspend TUI and run SSH in foreground
            with self.suspend():
                subprocess.run(cmd)

        self._rebuild_tree()


# ── entry point ───────────────────────────────────────────────────────────

def main() -> None:
    import sys

    # If tmux is available but we're not inside it,
    # offer to relaunch inside tmux (unless --no-tmux flag)
    if "--no-tmux" not in sys.argv and tmux_mgr.has_tmux() and not tmux_mgr.inside_tmux():
        # Auto-launch inside tmux for the full experience
        tmux_mgr.relaunch_in_tmux()
        return  # unreachable if exec succeeds

    # Remove our flag so textual doesn't see it
    sys.argv = [a for a in sys.argv if a != "--no-tmux"]

    app = SSHManagerApp()
    app.run()


if __name__ == "__main__":
    main()
