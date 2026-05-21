from __future__ import annotations

import boto3
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from src.ui.views.cluster_list import ClusterListView


class DocDBApp(App):
    TITLE = "Amazon DocumentDB"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, session: boto3.Session) -> None:
        super().__init__()
        self.session = session

    def compose(self) -> ComposeResult:
        yield Header()
        yield ClusterListView(self.session)
        yield Footer()


def run(session: boto3.Session) -> None:
    app = DocDBApp(session)
    app.run()
