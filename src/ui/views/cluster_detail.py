from __future__ import annotations

import boto3
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.widgets import DataTable, Static

from src.aws.cloudwatch import get_instance_metrics, get_volume_bytes_used
from src.aws.docdb import get_cluster_detail, list_instances


class ClusterDetailView(Container):
    DEFAULT_CSS = """
    ClusterDetailView {
        layout: vertical;
    }
    #cluster-info {
        height: auto;
        max-height: 14;
    }
    #instance-section-title {
        height: auto;
        margin-top: 1;
        margin-bottom: 1;
    }
    #instance-table {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, session: boto3.Session, cluster_id: str) -> None:
        super().__init__()
        self.session = session
        self.cluster_id = cluster_id

    def compose(self) -> ComposeResult:
        yield Static(id="cluster-info")
        yield Static("Instances", id="instance-section-title", classes="title")
        yield DataTable(id="instance-table")

    def on_mount(self) -> None:
        table = self.query_one("#instance-table", DataTable)
        table.add_columns(
            "Instance", "Status", "Role", "Region & AZ",
            "Instance Class", "CPU %", "Connections",
        )
        table.cursor_type = "row"
        self._load_data()

    def _load_data(self) -> None:
        info_panel = self.query_one("#cluster-info", Static)

        try:
            detail = get_cluster_detail(self.session, self.cluster_id)
            volume = get_volume_bytes_used(self.session, [self.cluster_id])
            bytes_used = volume.get(self.cluster_id)
            storage_gb = f"{bytes_used / (1024 ** 3):.1f} GB" if bytes_used is not None else "—"

            lines = [
                f"  Cluster:          {detail['id']}",
                f"  Status:           {detail['status']}",
                f"  Engine Version:   {detail['engine_version']}",
                f"  Storage Type:     {detail['storage_type']}",
                f"  Storage (GB):     {storage_gb}",
                f"  Instances:        {detail['instance_count']}",
                f"  Parameter Group:  {detail['parameter_group']} ({detail['parameter_group_status']})",
                f"  Endpoint:         {detail['endpoint']}:{detail['port']}",
                f"  Reader Endpoint:  {detail['reader_endpoint']}:{detail['port']}",
            ]
            info_panel.update("\n".join(lines))
        except Exception as e:
            info_panel.update(f"  Error loading cluster: {e}")

        self._load_instances()

    def _load_instances(self) -> None:
        table = self.query_one("#instance-table", DataTable)
        table.clear()
        try:
            instances = list_instances(self.session, self.cluster_id)
            instance_ids = [inst["id"] for inst in instances]
            metrics = get_instance_metrics(self.session, instance_ids)

            for inst in instances:
                inst_metrics = metrics.get(inst["id"], {})
                cpu = inst_metrics.get("cpu_percent")
                cpu_str = f"{cpu:.1f}" if cpu is not None else "—"
                conns = inst_metrics.get("connections")
                conns_str = str(conns) if conns is not None else "—"
                region_az = f"{inst['region']}/{inst['az']}" if inst["region"] else inst["az"]

                table.add_row(
                    inst["id"],
                    inst["status"],
                    inst["role"],
                    region_az,
                    inst["instance_class"],
                    Text(cpu_str, justify="right"),
                    Text(conns_str, justify="right"),
                )
        except Exception as e:
            self.notify(f"Error loading instances: {e}", severity="error")

    def action_refresh(self) -> None:
        self._load_data()
        self.notify("Refreshed")

    def action_go_back(self) -> None:
        self.app.pop_screen()
