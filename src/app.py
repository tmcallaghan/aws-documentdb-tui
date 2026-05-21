from __future__ import annotations

import boto3
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header

from src.ui.views.cluster_detail import ClusterDetailView
from src.ui.views.cluster_list import ClusterListView


class ClusterListScreen(Screen):
    BINDINGS = [
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, session: boto3.Session) -> None:
        super().__init__()
        self.session = session

    def compose(self) -> ComposeResult:
        yield Header()
        yield ClusterListView(self.session)
        yield Footer()

    def action_quit_app(self) -> None:
        self.app.exit()


class ClusterDetailScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
    ]

    def __init__(self, session: boto3.Session, cluster_id: str) -> None:
        super().__init__()
        self.session = session
        self.cluster_id = cluster_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield ClusterDetailView(self.session, self.cluster_id)
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()


class DocDBApp(App):
    TITLE = "Amazon DocumentDB"

    def __init__(self, session: boto3.Session) -> None:
        super().__init__()
        self.session = session

    def on_mount(self) -> None:
        self.push_screen(ClusterListScreen(self.session))


def run(session: boto3.Session) -> None:
    app = DocDBApp(session)
    app.run()
