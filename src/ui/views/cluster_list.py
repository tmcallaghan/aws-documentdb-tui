from __future__ import annotations

import boto3
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from rich.text import Text
from textual.widgets import DataTable, Static

from src.aws.cloudwatch import get_volume_bytes_used
from src.aws.docdb import list_clusters


class ClusterListView(Container):
    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, session: boto3.Session) -> None:
        super().__init__()
        self.session = session

    def compose(self) -> ComposeResult:
        yield Static("DocumentDB Clusters", classes="title")
        yield DataTable(id="cluster-table")

    def on_mount(self) -> None:
        table = self.query_one("#cluster-table", DataTable)
        table.add_columns("Cluster ID", "Status", "Engine Version", "Instances", "Storage (GB)", "Storage Type", "Parameter Group")
        table.cursor_type = "row"
        self._load_data()

    def _load_data(self) -> None:
        table = self.query_one("#cluster-table", DataTable)
        table.clear()
        try:
            clusters = list_clusters(self.session)
            cluster_ids = [c["id"] for c in clusters]
            volume_sizes = get_volume_bytes_used(self.session, cluster_ids)
            for c in clusters:
                bytes_used = volume_sizes.get(c["id"])
                storage_gb = f"{bytes_used / (1024 ** 3):.1f}" if bytes_used is not None else "—"
                table.add_row(
                    c["id"],
                    c["status"],
                    c["engine_version"],
                    Text(str(c["instance_count"]), justify="right"),
                    Text(storage_gb, justify="right"),
                    c["storage_type"],
                    c["parameter_group"],
                )
        except Exception as e:
            self.notify(f"Error loading clusters: {e}", severity="error")

    def action_refresh(self) -> None:
        self._load_data()
        self.notify("Refreshed")
