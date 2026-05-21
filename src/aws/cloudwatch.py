from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import boto3


def get_volume_bytes_used(session: boto3.Session, cluster_ids: list[str]) -> dict[str, float]:
    """Returns a mapping of cluster_id -> volume bytes used (latest value)."""
    if not cluster_ids:
        return {}

    client = session.client("cloudwatch")
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=6)

    queries = []
    for i, cluster_id in enumerate(cluster_ids):
        queries.append({
            "Id": f"m{i}",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/DocDB",
                    "MetricName": "VolumeBytesUsed",
                    "Dimensions": [
                        {"Name": "DBClusterIdentifier", "Value": cluster_id},
                    ],
                },
                "Period": 300,
                "Stat": "Average",
            },
        })

    result = {}
    # GetMetricData accepts max 500 queries per call
    for batch_start in range(0, len(queries), 500):
        batch = queries[batch_start : batch_start + 500]
        response = client.get_metric_data(
            MetricDataQueries=batch,
            StartTime=start,
            EndTime=now,
        )
        for metric in response["MetricDataResults"]:
            idx = int(metric["Id"][1:])
            cluster_id = cluster_ids[batch_start + idx]
            if metric["Values"]:
                result[cluster_id] = metric["Values"][0]

    return result


def get_instance_metrics(
    session: boto3.Session, instance_ids: list[str]
) -> dict[str, dict[str, Any]]:
    """Returns a mapping of instance_id -> {cpu_percent, connections}."""
    if not instance_ids:
        return {}

    client = session.client("cloudwatch")
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=1)

    queries = []
    for i, instance_id in enumerate(instance_ids):
        queries.append({
            "Id": f"cpu{i}",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/DocDB",
                    "MetricName": "CPUUtilization",
                    "Dimensions": [
                        {"Name": "DBInstanceIdentifier", "Value": instance_id},
                    ],
                },
                "Period": 300,
                "Stat": "Average",
            },
        })
        queries.append({
            "Id": f"conn{i}",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/DocDB",
                    "MetricName": "DatabaseConnections",
                    "Dimensions": [
                        {"Name": "DBInstanceIdentifier", "Value": instance_id},
                    ],
                },
                "Period": 300,
                "Stat": "Average",
            },
        })

    result: dict[str, dict[str, Any]] = {iid: {} for iid in instance_ids}

    for batch_start in range(0, len(queries), 500):
        batch = queries[batch_start : batch_start + 500]
        response = client.get_metric_data(
            MetricDataQueries=batch,
            StartTime=start,
            EndTime=now,
        )
        for metric in response["MetricDataResults"]:
            metric_id = metric["Id"]
            if metric_id.startswith("cpu"):
                idx = int(metric_id[3:])
                instance_id = instance_ids[idx]
                if metric["Values"]:
                    result[instance_id]["cpu_percent"] = metric["Values"][0]
            elif metric_id.startswith("conn"):
                idx = int(metric_id[4:])
                instance_id = instance_ids[idx]
                if metric["Values"]:
                    result[instance_id]["connections"] = int(metric["Values"][0])

    return result
