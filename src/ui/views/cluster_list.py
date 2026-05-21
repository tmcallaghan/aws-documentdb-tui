from __future__ import annotations

import boto3
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import DataTable, Static

from src.aws.cloudwatch import get_volume_bytes_used
from src.aws.docdb import list_clusters


class ClusterListView(Container):
    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("enter", "select_cluster", "Open", show=False),
    ]

    def __init__(self, session: boto3.Session) -> None:
        super().__init__()
        self.session = session
        self._cluster_ids: list[str] = []

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
        self._cluster_ids = []
        try:
            clusters = list_clusters(self.session)
            cluster_ids = [c["id"] for c in clusters]
            volume_sizes = get_volume_bytes_used(self.session, cluster_ids)
            for c in clusters:
                self._cluster_ids.append(c["id"])
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

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._open_cluster(event.cursor_row)

    def action_select_cluster(self) -> None:
        table = self.query_one("#cluster-table", DataTable)
        self._open_cluster(table.cursor_row)

    def _open_cluster(self, row_index: int) -> None:
        if 0 <= row_index < len(self._cluster_ids):
            from src.app import ClusterDetailScreen
            cluster_id = self._cluster_ids[row_index]
            self.app.push_screen(ClusterDetailScreen(self.session, cluster_id))

    def action_refresh(self) -> None:
        self._load_data()
        self.notify("Refreshed")
